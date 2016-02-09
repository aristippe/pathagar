import os
import errno

from django.conf import settings
from django.core.files import File
from django.core.files.move import _samefile
from django.core.files.storage import FileSystemStorage


def file_symlink_safe(old_file_name, new_file_name, allow_overwrite=False):
    """
    Create a symbolic link to `old_file_name` from `new_file_name`.

    Might raise NotImplemented if the system does not support symbolic links,
    and IOError or other Exceptions thrown by os.symlink.
    """
    # Make sure the system has support for symbolic links.
    # TODO: detect it with more precision, check for other platforms.
    if os.name != 'posix':
        raise NotImplemented('System %s does not support symbolic links' %
                             os.name)

    # There's no reason to move if we don't have to.
    if _samefile(old_file_name, new_file_name):
        return

    # Create the symbolic link.
    os.symlink(old_file_name, new_file_name)


class LinkableFile(File):
    """`File` subclass, used as a way of determining if the symbolic link
    logic on is invoked during `LinkOrFileSystemStorage._save()`.
    Note that this class should always be instantiated with an absolute path.
    """
    pass


class LinkOrFileSystemStorage(FileSystemStorage):
    """Storage that creates a symbolic link instead of copying the file is
    the file to be saved is a `LinkableFile`.
    For regular `File`s, and if the system does not support symbolic links or
    the generation of the symbolic link failed for any reason, the behavior
    is the same as `FileSystemStorage` (ie. copy the file).

    It's meant to be used in conjunction with `LinkableFile`:
        > storage = LinkOrFileSystemStorage(...)
        > storage.save('x/symlink_file', LinkableFile(open('/x/srcfile')))
        > storage.save('x/regular_file', File(open('/x/srcfile')))

        'x/symlink_file' == symbolic link to /x/srcfile
        'x/regular_file' == copy of /x/srcfile

    TODO: delete() relies on os.remove(), which seems to be fine, but might
    be worth checking if under ancient Python versions or similar it causes
    the *original* file to be removed.
    """
    def _save(self, name, content):
        """Save the object using a symlink, and in case of errors, fall back
        to saving it using a regular copy.
        """
        print 'XXXXX: %s' % self.path(name)
        try:
            return self._save_symlink(name, content)
        except:
            return super(LinkOrFileSystemStorage, self)._save(name, content)

    def _save_symlink(self, name, content):
        """Save the object using a symbolic link. Will raise a `TypeError`
        if `content` is not a `LinkableFile`.

        This method is basically a straight copy of FileSystemStorage._save(),
        with the extra check for `LinkableFile` at the top, and removing
        unusued logic in the `while` loop.

        TODO: when upgrading Django, check if FileSystemStorage._save() has
        changed and update this method accordingly.
        """
        # Raise an exception if not applicable.
        if not isinstance(content, LinkableFile):
            raise TypeError('%s is not a LinkableFile')

        full_path = self.path(name)

        # Create any intermediate directories that do not exist.
        # Note that there is a race between os.path.exists and os.makedirs:
        # if os.makedirs fails with EEXIST, the directory was created
        # concurrently, and we can continue normally. Refs #16082.
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
        if not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        # There's a potential race condition between get_available_name and
        # saving the file; it's possible that two threads might return the
        # same name, at which point all sorts of fun happens. So we need to
        # try to create the file, but if it already exists we have to go back
        # to get_available_name() and try again.

        while True:
            try:
                # The LinkableFile is assumed to always have an absolute path.
                file_symlink_safe(content.name, full_path)
            except OSError, e:
                if e.errno == errno.EEXIST:
                    # Ooops, the file exists. We need a new file name.
                    name = self.get_available_name(name)
                    full_path = self.path(name)
                else:
                    raise
            else:
                # OK, the file save worked. Break out of the loop.
                break

        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)

        return name

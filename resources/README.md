Sample ePubs
------------
At `resources/epubsamples`:

| File                         | Valid              | Cover              | Description                                        | Source                                |
|------------------------------|--------------------|--------------------|----------------------------------------------------|---------------------------------------|
| epub30-spec.epub             | :white_check_mark: | :white_check_mark: | EPUB 3.0 Specification                             | https://github.com/IDPF/epub3-samples |
| figure-gallery-bindings.epub | :white_check_mark: | :white_check_mark: | Figure Gallery                                     | https://github.com/IDPF/epub3-samples |
| hefty-water.epub             | :white_check_mark: |                    |                                                    | https://github.com/IDPF/epub3-samples |
| israelsailing.epub           | :white_check_mark: |                    | EPUB 3; EPUB 2 spec cover of type "cover" in guide | https://github.com/IDPF/epub3-samples |
| missing-cover.epub           | :white_check_mark: |                    | epub30-spec.epub w/removed cover                   | https://github.com/IDPF/epub3-samples |
| not-an-epub-but-a-zip.epub   |                    |                    | Invalid file, zipped version of `not-an-epub.epub` |                                       |
| not-an-epub.epub             |                    |                    | Invalid file with the string `I'm not an epub!`    |                                       |

Adding a sample ePub
--------------------
* Copy it to `resources/epubsamples`.
* Append it to `EPUBS_ALL` on `books/tests/sample_epubs.py`.
* Check that the tests are successful.
* Update this page!

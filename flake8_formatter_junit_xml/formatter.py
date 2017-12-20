from __future__ import print_function
from flake8.formatting import default
from junit_xml import TestSuite, TestCase


class JUnitXmlFormatter(default.Default):
    """JUnit XML formatter for Flake8."""

    test_suites = dict()

    def after_init(self):
        self.options.format = "default" # so that DefaultFormatter uses their built-in format
        super().after_init()

    def beginning(self, filename):
        name = '{0}.{1}'.format("flake8", filename.replace('.', '_'))
        self.test_suites[filename] = TestSuite(name, file=filename)

    # Store each error as a TestCase
    def handle(self, error):
        name = '{0}, {1}'.format(error.code, error.text)
        test_case = TestCase(name, file=error.filename, line=error.line_number)
        message = '%(path)s:%(row)d:%(col)d: %(code)s %(text)s' % {
            "code": error.code,
            "text": error.text,
            "path": error.filename,
            "row": error.line_number,
            "col": error.column_number,
        }
        test_case.add_failure_info(message)
        self.test_suites[error.filename].test_cases.append(test_case)
        super().handle(error)

    # Only write to fd (unless None)
    def _write_fd(self, output):
        if self.output_fd is not None:
            self.output_fd.write(output + self.newline)

    # Only write to screen (if necessary)
    def _write(self, output):
        if self.output_fd is None or self.options.tee:
            print(output)

    # writes results to file after all files are processed
    def stop(self):
        self._write_fd(TestSuite.to_xml_string(iter(self.test_suites.values())))
        super().stop()

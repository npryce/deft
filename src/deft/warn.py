

class PrintWarnings(object):
    def __init__(self, _output, _prefix, **formats):
        self._output = _output
        self._prefix = _prefix
        self._formats = formats
    
    def __getattr__(self, warning_name):
        def print_warning(**kwargs):
            message = self._message_for(warning_name, kwargs)
            self._output.write(self._prefix)
            self._output.write(message)
            self._output.write("\n")
        return print_warning

    def _message_for(self, warning_name, args):
        if warning_name in self._formats:
            return self._formats[warning_name].format(**args)
        else:
            return fallback_format(warning_name, args)

    

def format_dict(d):
    return ", ".join(name + ": " + repr(value) for (name, value) in sorted(d.items()))


def fallback_format(warning_name, args):
    return warning_name.replace("_", " ") + (" (" + format_dict(args) + ")" if args else "")


class IgnoreWarnings(object):
    def __getattr__(self, warning_name):
        return self._ignore_warning
    
    @staticmethod
    def _ignore_warning(**kwargs):
        pass



class WarningRecorder(object):
    def __init__(self):
        self._warnings = []
    
    def __len__(self):
        return len(self._warnings)
    
    def __getitem__(self, i):
        return self._warnings[i]
    
    def __iter__(self):
        return iter(self._warnings)
    
    def __getattr__(self, warning_name):
        def record_warning(**kwargs):
            self._warnings.append((warning_name, kwargs))
        return record_warning



class WarningRaiser(object):
    def __init__(self, exception_to_raise=UserWarning):
        self._exception_to_raise = exception_to_raise
    
    def __getattr__(self, warning_name):
        def raise_warning(**kwargs):
            raise self._exception_to_raise(fallback_format(warning_name, kwargs))
        return raise_warning

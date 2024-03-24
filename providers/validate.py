from cerberus import Validator as CerberusValidator


class Validator:

    _create_validator_class = CerberusValidator

    def __init__(self, schema=None):
        self._validator = self._create_validator_class(schema, allow_unknown=True)

    def validate(self, document=None, to_bool=True, messages=None):
        if document is None or not isinstance(document, dict):
            document = {}

        validated = self._validator.validate(document)

        if to_bool:
            return True if to_bool else False

        if not validated:
            if messages is not None:
                return False, self.get_parsed_errors(messages)
            return False, self.get_errors()

        return True, self.get_document()

    def __parse_error_messages(self, messages):
        """
        validate error message map, example:
        {'key.min': 'customized message if key is min.'}
        :param messages: dict
        :return: dict
        """
        nm = {}
        errors = self.get_errors()
        for error_key, error_values in errors.items():
            ml = []
            for _k, _h in enumerate(self._validator.document_error_tree[error_key].errors):
                _key = '.'.join([error_key, _h.rule])
                if _key in messages:
                    _message = messages.get(_key)
                else:
                    _message = error_values[_k]
                ml.append(_message)
            nm[error_key] = ml
        return nm

    def get_parsed_errors(self, messages):
        return self.__parse_error_messages(messages)

    def get_errors(self):
        """
        validate failed
        get error message like:
        {'age': 'min value is 10'}
        """
        return self._validator.errors

    def get_document(self):
        """
        The normalization and coercion are performed on the copy of the original document
        and the result document is available via document-property.
        :return:
        """
        return self._validator.document

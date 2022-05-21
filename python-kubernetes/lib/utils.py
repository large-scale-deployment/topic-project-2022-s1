import six
import datetime


def construct_label_selectors(deployment):
    labels = [ f'{k}={v}' for k, v in deployment.spec.template.metadata.labels.items()]
    return ','.join(labels)

def sanitize_for_serialization(obj):
    """Builds a JSON POST object.

    If obj is None, return None.
    If obj is str, int, long, float, bool, return directly.
    If obj is datetime.datetime, datetime.date
        convert to string in iso8601 format.
    If obj is list, sanitize each element in the list.
    If obj is dict, return the dict.
    If obj is OpenAPI model, return the properties dict.

    :param obj: The data to serialize.
    :return: The serialized form of data.
    """

    PRIMITIVE_TYPES = (float, bool, bytes, six.text_type) + six.integer_types
    if obj is None:
        return None
    elif isinstance(obj, PRIMITIVE_TYPES):
        return obj
    elif isinstance(obj, list):
        return [sanitize_for_serialization(sub_obj)
                for sub_obj in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_for_serialization(sub_obj)
                      for sub_obj in obj)
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    if isinstance(obj, dict):
        obj_dict = obj
    else:
        # Convert model obj to dict except
        # attributes `openapi_types`, `attribute_map`
        # and attributes which value is not None.
        # Convert attribute name to json key in
        # model definition for request.
        obj_dict = {obj.attribute_map[attr]: getattr(obj, attr)
                    for attr, _ in six.iteritems(obj.openapi_types)
                    if getattr(obj, attr) is not None}

    return {key: sanitize_for_serialization(val)
            for key, val in six.iteritems(obj_dict)}
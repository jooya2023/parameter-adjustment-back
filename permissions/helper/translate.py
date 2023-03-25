from permissions.helper.translate_json import *


def translate_permission(perm: str):
    try:
        spatial_permission = spatial_permissions.get(perm.name)
        if spatial_permission:
            return spatial_permission

        translated_name_permission = []
        app = filtered_permissions.get(perm.content_type.app_label)
        model = app.get('models')
        split_name_permission = perm.name.split(" ", 2)
        # translated_name_permission.append(can.get(split_name_permission[0]))
        translated_name_permission.append(four_option_in_permission.get(split_name_permission[1]))
        translated_name_permission.append(model.get(split_name_permission[2].replace(' ', '')))
        result_translate = " "
        result_translate = result_translate.join(translated_name_permission)
        return result_translate
    except Exception:
        return ""

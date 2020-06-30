import sys
import os


def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s

# set(EMBED_FILES
# src/style.css src/jquery.gz src/code.js src/index.html src/ruuvi.html src/ruuvi.js src/ruuvi.css)


def main():
    script_name = os.path.split(sys.argv[0])[1]
    base_path = 'ruuvi.gwui.html/src'
    exclude_files = [
        'wifi_icon.png',
        'ruuvi_logo.svg',
    ]
    with open('embed_files.txt', 'w') as fd:
        fd.write(f'# This file was generated by {script_name}\n')
        fd.write('\n')
        fd.write('set(EMBED_FILES\n')
        for root, subdirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.json'):
                    continue
                if os.path.splitext(file)[1] == '':
                    continue
                if file in exclude_files:
                    continue
                if not file.endswith('.gz') and os.path.exists(f'{root}/{file}.gz'):
                    continue
                fd.write(f'        {root}/{file}\n')
        fd.write(')\n')
    with open('src/ruuvi_gwui_html.c', 'w') as fd:
        fd.write('/*\n')
        fd.write(f' * This file was generated by {script_name}\n')
        fd.write('*/\n')
        fd.write('#include "ruuvi_gwui_html.h"\n')
        fd.write('#include <string.h>\n')
        fd.write('\n')
        fd.write('/**\n')
        fd.write(' * @brief Find embedded file by path.\n')
        fd.write(' * @see https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/build-system.html#embedding-binary-data\n')
        fd.write(' */\n')
        fd.write('const uint8_t* embed_files_find(const char* file_path, size_t* pLen, bool* pIsGzipped)\n')
        fd.write('{\n')
        fd.write(f'    *pIsGzipped = false;\n')
        for root, subdirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.json'):
                    continue
                if os.path.splitext(file)[1] == '':
                    continue
                if file in exclude_files:
                    continue
                rel_root = remove_prefix(root, base_path)
                if rel_root.startswith('/'):
                    rel_root = remove_prefix(rel_root, '/')
                if len(rel_root) > 0:
                    rel_root += '/'
                fd.write(f'    if (0 == strcmp(file_path, "{rel_root}{file}"))\n')
                fd.write('    {\n')
                file_name_patched = file.replace('.', '_').replace('-', '_')
                if not file.endswith('.gz') and os.path.exists(f'{root}/{file}.gz'):
                    fd.write(f'        extern const uint8_t embedded_{file_name_patched}_start[] asm("_binary_{file_name_patched}_gz_start");\n')
                    fd.write(f'        extern const uint8_t embedded_{file_name_patched}_end[] asm("_binary_{file_name_patched}_gz_end");\n')
                    fd.write(f'        *pIsGzipped = true;\n')
                else:
                    fd.write(f'        extern const uint8_t embedded_{file_name_patched}_start[] asm("_binary_{file_name_patched}_start");\n')
                    fd.write(f'        extern const uint8_t embedded_{file_name_patched}_end[] asm("_binary_{file_name_patched}_end");\n')
                fd.write(f'        *pLen = embedded_{file_name_patched}_end - embedded_{file_name_patched}_start;\n')
                fd.write(f'        return embedded_{file_name_patched}_start;\n')
                fd.write('    }\n')
        fd.write('    *pLen = 0;\n')
        fd.write('    return NULL;\n')
        fd.write('}\n')
    pass


if __name__ == '__main__':
    main()

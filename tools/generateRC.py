import textwrap


def genMainRC(__version__, APP):
    APP = APP.replace("'", "\\'")

    version_str = __version__.split("-")[0]
    parts = (version_str.split(".") + ["0", "0", "0"])[:3]
    version = [int(p) if p.isdigit() else 0 for p in parts]

    a = f"""
    # UTF-8
    # Please refer to __version__.py
    # For more details about fixed file info 'ffi' see:
    # http://msdn.microsoft.com/en-us/library/ms646997.aspx
    VSVersionInfo(
      ffi=FixedFileInfo(
        # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
        # Set not needed items to zero 0.
        filevers=({version[0]}, {version[1]}, {version[2]}, 0),
        prodvers=({version[0]}, {version[1]}, {version[2]}, 0),
        # Contains a bitmask that specifies the valid bits 'flags'r
        mask=0x3f,
        # Contains a bitmask that specifies the Boolean attributes of the file.
        flags=0x0,
        # The operating system for which this file was designed.
        # 0x4 - NT and there is no need to change it.
        OS=0x4,
        # The general type of file.
        # 0x1 - the file is an application.
        fileType=0x1,
        # The function of the file.
        # 0x0 - the function is not defined for this fileType
        subtype=0x0,
        # Creation date and time stamp.
        date=(0, 0)
        ),
      kids=[
        StringFileInfo(
          [
          StringTable(
            '040904e4',
            [StringStruct('CompanyName', 'N8VENTURES'),
            StringStruct('FileDescription', '{APP}'),
            StringStruct('FileVersion', '{__version__}'),
            StringStruct('InternalName', 'APP'),
            StringStruct('LegalCopyright','Copyright © 2024-2026 John Nathaniel Calvara. Licensed under the MIT License.'),
            StringStruct('OriginalFilename', '{APP}.exe'),
            StringStruct('ProductName', '{APP}'),
            StringStruct('ProductVersion', '{__version__}')])
          ]), 
        VarFileInfo([VarStruct('Translation', [1033, 1252])])
      ]
    )
    """
    a = textwrap.dedent(a)
    with open(f"main.rc", "w", encoding="utf-8") as rc_file:
        rc_file.write(a.__str__())

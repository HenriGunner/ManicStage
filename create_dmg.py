from dmgbuild import build_dmg

# Build the DMG file
build_dmg(
    filename='Sony_Walkman_Repair.dmg',
    volume_name='Sony Walkman Repair',
    format='UDZO',
    files=['Sony Walkman Repair.app'],
    icon='Sony Walkman Repair.app/Contents/Resources/app_icon.icns' if True else None,
    symlink_paths=[],
    appdmg={
        'title': 'Sony Walkman Repair',
        'icon-size': 80,
        'window': {
            'position': {'x': 400, 'y': 300},
            'size': {'width': 500, 'height': 300}
        },
        'contents': [
            {'x': 150, 'y': 150, 'type': 'file', 'path': 'Sony Walkman Repair.app'},
            {'x': 350, 'y': 150, 'type': 'link', 'path': '/Applications'}
        ]
    }
)

print("DMG created successfully!")

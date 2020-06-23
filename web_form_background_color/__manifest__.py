# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# Copyright 2018 Brainbean Apps
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

{
    "name": "Form views custom background color",
    "summary": "Enable to change some models form's background color",
    "category": "Web",
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "Clément Mombereau",
    "website": "https://github.com/clementmbr/band-booking",
    "depends": [
        "web",
        "backend_theme_v12",  # https://github.com/Openworx/backend_theme
    ],
    "data": ["views/web_form_background_color.xml"],
    "installable": True,
}

import os

import PySimpleGUI as sg

sg.theme("Default1")
download_settings_tab = sg.Tab(
    "Download Settings",
    [
        [
            sg.Col(
                [
                    [
                        sg.Text("Audio Source:"),
                        sg.Combo(
                            [
                                "youtube",
                                "youtube-music",
                                "slider-kz",
                                "soundcloud",
                                "bandcamp",
                                "piped",
                            ],
                            key="AUDIO_SOURCE",
                            readonly=True,
                            default_value="youtube-music",
                            size=(20, 1),
                        ),
                        sg.Text("Lyrics Source:"),
                        sg.Combo(
                            ["genius", "musixmatch", "azlyrics", "synced"],
                            key="LYRICS_SOURCE",
                            readonly=True,
                            size=(20, 1),
                        ),
                    ],
                    [
                        sg.Text("Format:" + " " * 9),
                        sg.Combo(
                            ["mp3", "flac", "ogg", "opus", "m4a", "wav"],
                            key="FORMAT",
                            readonly=True,
                            default_value="mp3",
                            size=(20, 1),
                        ),
                        sg.Text("Bitrate:" + " " * 11),
                        sg.Combo(
                            [
                                "auto",
                                "disable",
                                "8k",
                                "16k",
                                "24k",
                                "32k",
                                "40k",
                                "48k",
                                "64k",
                                "80k",
                                "96k",
                                "112k",
                                "128k",
                                "160k",
                                "192k",
                                "224k",
                                "256k",
                                "320k",
                            ],
                            key="BITRATE",
                            readonly=True,
                            default_value="320k",
                            size=(20, 1),
                        ),
                    ],
                    [
                        sg.Text("FFmpeg Args:", size=(13, 1)),
                        sg.InputText(key="FFMPEG_ARGS", expand_x=True),
                    ],
                    [
                        sg.Text("Threads:"),
                        sg.Spin(
                            [i for i in range(1, os.cpu_count() + 1)],
                            initial_value=os.cpu_count(),
                            key="THREADS",
                            size=(2, 1),
                        ),
                        sg.Text("Log Level:"),
                        sg.Combo(
                            [
                                "CRITICAL",
                                "FATAL",
                                "ERROR",
                                "WARN",
                                "WARNING",
                                "INFO",
                                "MATCH",
                                "DEBUG",
                                "NOTSET",
                            ],
                            key="LOG_LEVEL",
                            default_value="INFO",
                            readonly=True,
                        ),
                    ],
                    [
                        sg.Multiline(
                            default_text="Output will be displayed here...",
                            expand_x=True,
                            expand_y=True,
                            key="OUTPUT",
                        )
                    ],
                ],
                expand_x=True,
                expand_y=True,
            )
        ]
    ],
)

# Advanced Settings Tab
advanced_settings_tab = sg.Tab(
    "Advanced Settings",
    [
        [
            sg.Col(
                [
                    [
                        sg.Checkbox(
                            "Don't Filter Results", key="NO_FILTER", size=(15, 1)
                        ),
                        sg.Checkbox(
                            "Only Verified Results",
                            key="VERIFIED_RESULTS",
                            size=(15, 1),
                        ),
                    ],
                    [
                        sg.Checkbox("Headless", key="HEADLESS", size=(15, 1)),
                        sg.Checkbox("No Cache", key="NO_CACHE", size=(15, 1)),
                        sg.Checkbox("Preload", key="PRELOAD", size=(15, 1)),
                    ],
                    [
                        sg.Checkbox("Save File", key="SAVE_FILE", size=(15, 1)),
                        sg.Checkbox(
                            "Use Cache File", key="USE_CACHE_FILE", size=(15, 1)
                        ),
                        sg.Checkbox("M3U Playlist", key="M3U", size=(15, 1)),
                    ],
                    [
                        sg.Checkbox("Fetch Albums", key="FETCH_ALBUMS", size=(15, 1)),
                        sg.Checkbox("Generate Lyrics", key="GEN_LYRICS", size=(15, 1)),
                        sg.Checkbox(
                            "Detect Formats", key="DETECT_FORMATS", size=(15, 1)
                        ),
                    ],
                    [
                        sg.Checkbox("Sponsor Block", key="SPONSOR_BLOCK", size=(15, 1)),
                        sg.Checkbox("Redownload", key="REDOWNLOAD", size=(15, 1)),
                        sg.Checkbox("Keep Alive", key="KEEP_ALIVE", size=(15, 1)),
                    ],
                    [
                        sg.Text("Max Retries:", size=(18, 1)),
                        sg.InputText(key="MAX_RETRIES"),
                    ],
                    [
                        sg.Text("Max Filename Length:", size=(18, 1)),
                        sg.InputText(key="MAX_FILENAME_LENGTH"),
                    ],
                    [
                        sg.Text("YT-DLP Args:", size=(18, 1)),
                        sg.InputText(key="YT_DLP_ARGS"),
                    ],
                ],
                expand_x=True,
                expand_y=True,
            )
        ]
    ],
)

# Connection Settings Tab
connection_settings_tab = sg.Tab(
    "Connection Settings",
    [
        [
            sg.Col(
                [
                    [
                        sg.Text("Proxy:", size=(10, 1)),
                        sg.InputText(key="PROXY", expand_x=True),
                    ],
                    [
                        sg.Text("Host:", size=(10, 1)),
                        sg.InputText(key="HOST", expand_x=True),
                    ],
                    [
                        sg.Text("Port:", size=(10, 1)),
                        sg.InputText(key="PORT", expand_x=True),
                    ],
                ]
            )
        ]
    ],
)

# Main Layout
layout = [
    [
        sg.Col(
            [
                [
                    sg.ProgressBar(
                        1,
                        orientation="h",
                        size=(20, 20),
                        expand_x=True,
                        expand_y=True,
                        key="PROGRESS_BAR",
                    )
                ],
                [
                    sg.Text("Spotify Playlist URL:", size=(15, 1)),
                    sg.InputText(key="URL", expand_y=True, expand_x=True),
                ],
                [
                    sg.Text("Output Directory:", size=(15, 1)),
                    sg.InputText(
                        key="OUTPUT-DIRECTORY",
                        expand_x=True,
                        default_text="Download",
                    ),
                    sg.FolderBrowse(),
                ],
                [
                    sg.TabGroup(
                        [
                            [
                                download_settings_tab,
                                advanced_settings_tab,
                                connection_settings_tab,
                            ]
                        ],
                        expand_x=True,
                    )
                ],
                [
                    sg.Col(
                        [
                            [
                                sg.Button("Download", key="-download-"),
                                sg.Button("Install/Check FFmpeg"),
                            ]
                        ],
                        justification="r",
                    )
                ],
            ]
        )
    ]
]

window = sg.Window(
    title="Spotify Playlist Downloader v.0.0.1",
    icon="statics/spotify.ico",
    layout=layout,
)

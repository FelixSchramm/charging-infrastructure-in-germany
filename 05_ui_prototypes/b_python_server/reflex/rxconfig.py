"""Reflex configuration of the overview prototype (issue #37)."""

import reflex as rx

config = rx.Config(
    app_name="overview",
    default_color_mode="light",
    telemetry_enabled=False,
    show_built_with_reflex=False,
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(accent_color="jade", gray_color="slate", radius="large")
        )
    ],
    disable_plugins=[rx.plugins.SitemapPlugin],
)

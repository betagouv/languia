from __future__ import annotations
from typing import Iterable
import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes
import time


class DSFR(Base):
    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = colors.neutral,
        secondary_hue: colors.Color | str = colors.neutral,
        neutral_hue: colors.Color | str = colors.neutral,
        spacing_size: sizes.Size | str = sizes.spacing_md,
        radius_size: sizes.Size | str = sizes.radius_none,
        text_size: sizes.Size | str = sizes.text_lg,
        font: fonts.Font | str | Iterable[fonts.Font | str] = (
            "Marianne",
            "Arial",
            "ui-sans-serif",
            "sans-serif",
        ),
        font_mono: fonts.Font | str | Iterable[fonts.Font | str] = (
            "Marianne",
            "Arial",
            "ui-sans-serif",
            "sans-serif",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            text_size=text_size,
            font=font,
            font_mono=font_mono,
        )

import os
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

# Ajuste o nome e caminho da fonte conforme seu projeto
ICON_FONT_FILENAME = 'fa-solid-900.ttf'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_FONT_PATH = os.path.join(CURRENT_DIR, ICON_FONT_FILENAME)
REGISTERED_ICON_FONT_NAME = "fa-solid-900"

if os.path.exists(ICON_FONT_PATH):
    LabelBase.register(name=REGISTERED_ICON_FONT_NAME, fn_regular=ICON_FONT_PATH)
else:
    print(f"[WARNING] Fonte de ícones '{ICON_FONT_PATH}' NÃO ENCONTRADA. Ícones podem não aparecer.")

class PalavrasListaApp(MDApp):
    def build(self):
        Window.clearcolor = (0.85, 0.92, 1, 1)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        container.bind(minimum_height=container.setter('height'))

        # Lê o arquivo palavrasalva.txt
        caminho = os.path.join(CURRENT_DIR, "palavrasalva.txt")
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha:
                        continue
                    partes = linha.split(maxsplit=1)
                    palavra = partes[0]
                    icone = partes[1] if len(partes) > 1 else ""

                    # Card para cada palavra+ícone
                    card = MDCard(
                        orientation='horizontal',
                        padding=dp(16),
                        spacing=dp(20),
                        size_hint_y=None,
                        height=dp(80),
                        md_bg_color=get_color_from_hex("#FFFFFF"),
                        radius=[15]
                    )
                    # Ícone
                    card.add_widget(MDLabel(
                        text=icone,
                        font_size="40sp",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex("#6A0DAD"),
                        size_hint_x=None,
                        width=dp(60),
                        halign="center",
                        valign="middle"
                    ))
                    # Palavra
                    card.add_widget(MDLabel(
                        text=palavra,
                        font_size="28sp",
                        halign="left",
                        valign="middle",
                        theme_text_color="Primary"
                    ))
                    container.add_widget(card)
        else:
            container.add_widget(Label(text="Arquivo palavrasalva.txt não encontrado.", color=(1,0,0,1)))

        scroll.add_widget(container)
        layout.add_widget(scroll)
        return layout

if __name__ == '__main__':
    PalavrasListaApp().run()
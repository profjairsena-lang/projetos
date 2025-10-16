import os
import json
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

CURRENT_DIR = os.path.dirname(__file__)
ARQUIVO_PALAVRAS = os.path.join(CURRENT_DIR, "palavras.json")


class IconeExibidorApp(App):
    def build(self):
        self.layout_principal = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Fundo da janela principal
        with self.layout_principal.canvas.before:
            Color(0.9, 0.85, 1, 1)  # Azul muito claro
            fundo = RoundedRectangle(size=self.layout_principal.size, pos=self.layout_principal.pos)
        self.layout_principal.bind(size=lambda inst, val: setattr(fundo, 'size', val))
        self.layout_principal.bind(pos=lambda inst, val: setattr(fundo, 'pos', val))

        # Campo de texto para a palavra
        self.input_palavra = TextInput(
            hint_text="Digite uma palavra para buscar...",
            multiline=False,
            font_size=20,
            size_hint=(1, None),
            height=dp(50),
            background_normal='',
            background_color=(0.95, 0.95, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.layout_principal.add_widget(self.input_palavra)

        # Área de exibição do ícone e palavra
        self.exibicao_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, None), height=dp(250))
        self.layout_principal.add_widget(self.exibicao_layout)

        # Botão de ação
        btn_exibir = Button(
            text="Mostrar Palavra e Ícone",
            background_normal='',
            background_color=(0.1, 0.4, 0.8, 1),
            font_size=22,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(50)
        )
        btn_exibir.bind(on_release=self.buscar_palavra)
        self.layout_principal.add_widget(btn_exibir)

        return self.layout_principal

    def buscar_palavra(self, instance):
        palavra_busca = self.input_palavra.text.strip().lower()
        self.exibicao_layout.clear_widgets()

        if not palavra_busca:
            self._mostrar_mensagem("[Digite uma palavra!]")
            return

        if not os.path.exists(ARQUIVO_PALAVRAS):
            self._mostrar_mensagem("[Arquivo não encontrado]")
            return

        try:
            with open(ARQUIVO_PALAVRAS, "r", encoding="utf-8") as f:
                dados = json.load(f)

            encontrado = None
            for item in dados:
                if item.get("palavra", "").lower() == palavra_busca:
                    encontrado = item
                    break

            if not encontrado:
                self._mostrar_mensagem(f"[Palavra '{palavra_busca}' não encontrada]")
                return

            caminho_icone = encontrado.get("icone", "")
            texto_palavra = encontrado.get("palavra", "Sem Palavra")

            if caminho_icone and os.path.exists(caminho_icone):
                img = Image(source=caminho_icone, size_hint=(None, None), size=(dp(130), dp(130)))
                icone_container = BoxLayout(size_hint_y=None, height=dp(140))
                icone_container.add_widget(img)
                self.exibicao_layout.add_widget(icone_container)

                label = Label(
                    text=texto_palavra,
                    font_size=30,
                    color=(0, 0, 0, 1),
                    size_hint_y=None,
                    height=dp(40)
                )
                texto_container = BoxLayout(size_hint_y=None, height=dp(50))
                texto_container.add_widget(label)
                self.exibicao_layout.add_widget(texto_container)
            else:
                self._mostrar_mensagem("[Ícone não encontrado]")

        except Exception as e:
            self._mostrar_mensagem(f"[Erro: {str(e)}]")

    def _mostrar_mensagem(self, texto):
        msg_label = Label(
            text=texto,
            font_size=20,
            color=(1, 0, 0, 1),
            size_hint_y=None,
            height=dp(40)
        )
        self.exibicao_layout.add_widget(msg_label)


if __name__ == '__main__':
    IconeExibidorApp().run()

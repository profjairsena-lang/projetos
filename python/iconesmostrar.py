import os
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

# Pasta onde estão os ícones em PNG
PASTA_EMOJIS = os.path.join(os.path.dirname(__file__), "emojis")

class SimpleIconImageApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_icon_path = None
        self.icon_display = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        Window.clearcolor = (0.94, 0.97, 1, 1)

        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        # Imagem principal do ícone selecionado
        self.icon_display = Image(source="", size_hint_y=None, height=dp(180))
        layout.add_widget(self.icon_display)

        btn_escolher = MDRaisedButton(text="Escolher Ícone", size_hint_y=None, height=dp(50))
        btn_escolher.bind(on_release=self.abrir_popup_icones)
        layout.add_widget(btn_escolher)

        btn_popup = MDRaisedButton(text="Mostrar Ícone no Popup", size_hint_y=None, height=dp(50))
        btn_popup.bind(on_release=self.mostrar_popup)
        layout.add_widget(btn_popup)

        return layout

    def abrir_popup_icones(self, instance):
        arquivos = [f for f in os.listdir(PASTA_EMOJIS) if f.endswith('.png')]
        grid = GridLayout(cols=5, spacing=10, padding=10)

        for nome in arquivos:
            caminho = os.path.join(PASTA_EMOJIS, nome)
            img_btn = Button(background_normal=caminho, size_hint=(None, None), size=(60, 60))
            img_btn.bind(on_release=lambda btn, c=caminho: self.selecionar_icone(c))
            grid.add_widget(img_btn)

        popup = Popup(title="Escolha um ícone", content=grid, size_hint=(None, None), size=(400, 300))
        self._popup = popup
        popup.open()

    def selecionar_icone(self, caminho):
        self.selected_icon_path = caminho
        self.icon_display.source = caminho
        if hasattr(self, '_popup'):
            self._popup.dismiss()

    def mostrar_popup(self, instance):
        if self.selected_icon_path:
            layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            img = Image(source=self.selected_icon_path, size_hint_y=None, height=dp(150))
            layout.add_widget(img)

            fechar_btn = MDRaisedButton(text="Fechar", on_release=lambda x: dialog.dismiss())
            layout.add_widget(fechar_btn)

            dialog = MDDialog(
                title="Ícone Escolhido",
                type="custom",
                content_cls=layout,
                size_hint=(0.7, 0.7)
            )
            dialog.open()
        else:
            self._dialog_alerta("Nenhum Ícone", "Selecione um ícone antes de abrir o popup.")

    def _dialog_alerta(self, titulo, texto):
        dialog = MDDialog(
            title=titulo,
            text=texto,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

if __name__ == '__main__':
    SimpleIconImageApp().run()

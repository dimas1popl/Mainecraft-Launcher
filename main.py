import customtkinter as ctk
import minecraft_launcher_lib as mclib
import subprocess
import threading
import os
from PIL import Image, ImageTk
import requests

# Настройка темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MinecraftLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Launcher")
        self.geometry("900x700")
        self.minecraft_dir = os.path.join(os.getenv('APPDATA'), '.minecraft')

        # Создаем директорию, если не существует
        os.makedirs(self.minecraft_dir, exist_ok=True)

        # Создание вкладок
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.play_tab = self.tabview.add("🎮 Играть")
        self.versions_tab = self.tabview.add("📦 Версии")
        self.settings_tab = self.tabview.add("⚙️ Настройки")

        self.setup_play_tab()
        self.setup_versions_tab()
        self.setup_settings_tab()

        # Загрузка версий
        self.load_installed_versions()
        self.load_available_versions()

    def setup_play_tab(self):
        # Заголовок
        title_label = ctk.CTkLabel(self.play_tab, text="Minecraft Launcher",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # Фрейм для выбора версии
        version_frame = ctk.CTkFrame(self.play_tab)
        version_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(version_frame, text="Выберите версию:",
                     font=ctk.CTkFont(weight="bold")).pack(pady=10)

        self.version_var = ctk.StringVar()
        self.version_dropdown = ctk.CTkComboBox(version_frame,
                                                variable=self.version_var,
                                                width=300)
        self.version_dropdown.pack(pady=10)

        # Прогресс-бар для установки
        self.progress_bar = ctk.CTkProgressBar(self.play_tab, height=20)
        self.progress_bar.pack(pady=5, padx=20, fill="x")
        self.progress_bar.set(0)

        # Кнопка запуска
        self.play_button = ctk.CTkButton(self.play_tab,
                                         text="🚀 Запустить Minecraft",
                                         command=self.launch_game,
                                         height=40,
                                         font=ctk.CTkFont(size=16))
        self.play_button.pack(pady=20)

        # Консоль вывода
        console_label = ctk.CTkLabel(self.play_tab, text="Лог запуска:")
        console_label.pack(pady=(20, 5))

        self.console = ctk.CTkTextbox(self.play_tab, height=200)
        self.console.pack(pady=10, fill="both", expand=True)

    def setup_versions_tab(self):
        # Создаем две вкладки внутри вкладки версий
        self.versions_tabview = ctk.CTkTabview(self.versions_tab)
        self.versions_tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.installed_tab = self.versions_tabview.add("Установленные")
        self.available_tab = self.versions_tabview.add("Доступные")

        # Установленные версии
        self.installed_versions_frame = ctk.CTkScrollableFrame(self.installed_tab)
        self.installed_versions_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Доступные версии
        self.available_versions_frame = ctk.CTkScrollableFrame(self.available_tab)
        self.available_versions_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки обновления
        refresh_frame = ctk.CTkFrame(self.versions_tab)
        refresh_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(refresh_frame, text="Обновить список",
                      command=self.load_all_versions).pack(side="left", padx=5)

    def setup_settings_tab(self):
        # Настройки памяти
        memory_frame = ctk.CTkFrame(self.settings_tab)
        memory_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(memory_frame, text="Настройки памяти",
                     font=ctk.CTkFont(weight="bold")).pack(pady=10)

        memory_subframe = ctk.CTkFrame(memory_frame)
        memory_subframe.pack(pady=10)

        ctk.CTkLabel(memory_subframe, text="Минимум (MB):").grid(row=0, column=0, padx=5, pady=5)
        self.min_memory = ctk.CTkEntry(memory_subframe, width=100)
        self.min_memory.insert(0, "2048")
        self.min_memory.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(memory_subframe, text="Максимум (MB):").grid(row=0, column=2, padx=5, pady=5)
        self.max_memory = ctk.CTkEntry(memory_subframe, width=100)
        self.max_memory.insert(0, "4096")
        self.max_memory.grid(row=0, column=3, padx=5, pady=5)

        # Путь к игре
        path_frame = ctk.CTkFrame(self.settings_tab)
        path_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(path_frame, text="Директория игры",
                     font=ctk.CTkFont(weight="bold")).pack(pady=10)

        path_subframe = ctk.CTkFrame(path_frame)
        path_subframe.pack(pady=10, fill="x", padx=10)

        self.dir_entry = ctk.CTkEntry(path_subframe, width=400)
        self.dir_entry.insert(0, self.minecraft_dir)
        self.dir_entry.pack(side="left", padx=5, pady=5)

        ctk.CTkButton(path_subframe, text="Обзор",
                      command=self.browse_directory).pack(side="left", padx=5)

        # Кнопка сохранения настроек
        ctk.CTkButton(self.settings_tab, text="Сохранить настройки",
                      command=self.save_settings).pack(pady=20)

    def browse_directory(self):
        from tkinter import filedialog
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            self.minecraft_dir = directory
            self.load_all_versions()

    def save_settings(self):
        self.minecraft_dir = self.dir_entry.get()
        self.log("Настройки сохранены!")
        self.load_all_versions()

    def load_all_versions(self):
        self.load_installed_versions()
        self.load_available_versions()

    def load_installed_versions(self):
        """Загрузка установленных версий"""
        threading.Thread(target=self._load_installed_versions_thread, daemon=True).start()

    def _load_installed_versions_thread(self):
        try:
            versions = mclib.utils.get_installed_versions(self.minecraft_dir)
            version_ids = [v['id'] for v in versions]

            # Обновляем интерфейс в основном потоке
            self.after(0, self._update_installed_versions, versions)
            self.after(0, self._update_version_dropdown, version_ids)

        except Exception as e:
            self.after(0, self.log, f"Ошибка загрузки установленных версий: {str(e)}")

    def _update_installed_versions(self, versions):
        """Обновление списка установленных версий в UI"""
        # Очищаем старый список
        for widget in self.installed_versions_frame.winfo_children():
            widget.destroy()

        if not versions:
            label = ctk.CTkLabel(self.installed_versions_frame,
                                 text="Нет установленных версий")
            label.pack(pady=20)
            return

        for version in versions:
            self._create_version_card(version, self.installed_versions_frame, True)

    def load_available_versions(self):
        """Загрузка доступных версий"""
        threading.Thread(target=self._load_available_versions_thread, daemon=True).start()

    def _load_available_versions_thread(self):
        try:
            # Получаем список всех версий
            version_list = mclib.utils.get_version_list()
            # Берем только последние 20 версий для примера
            recent_versions = version_list[:20]

            self.after(0, self._update_available_versions, recent_versions)

        except Exception as e:
            self.after(0, self.log, f"Ошибка загрузки доступных версий: {str(e)}")

    def _update_available_versions(self, versions):
        """Обновление списка доступных версий в UI"""
        for widget in self.available_versions_frame.winfo_children():
            widget.destroy()

        for version in versions:
            self._create_version_card(version, self.available_versions_frame, False)

    def _create_version_card(self, version, parent, is_installed):
        """Создание карточки версии"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5, padx=5)

        # Информация о версии
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ctk.CTkLabel(info_frame, text=version['id'],
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        version_type = version.get('type', 'unknown')
        color = "green" if version_type == "release" else "yellow" if version_type == "snapshot" else "gray"
        ctk.CTkLabel(info_frame, text=version_type, text_color=color).pack(anchor="w")

        # Кнопки действий
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(side="right", padx=5, pady=5)

        if is_installed:
            ctk.CTkButton(btn_frame, text="Удалить", width=80,
                          command=lambda v=version['id']: self.delete_version(v)).pack(side="left", padx=2)
        else:
            ctk.CTkButton(btn_frame, text="Установить", width=80,
                          command=lambda v=version['id']: self.install_version(v)).pack(side="left", padx=2)

    def _update_version_dropdown(self, version_ids):
        """Обновление выпадающего списка версий"""
        self.version_dropdown.configure(values=version_ids)
        if version_ids:
            self.version_var.set(version_ids[0])

    def install_version(self, version_id):
        """Установка версии"""
        threading.Thread(target=self._install_version_thread, args=(version_id,), daemon=True).start()

    def _install_version_thread(self, version_id):
        try:
            self.after(0, self.log, f"Начата установка версии {version_id}...")

            # Создаем callback для отслеживания прогресса
            callback = {
                'setStatus': lambda status: self.after(0, self.log, f"Статус: {status}"),
                'setProgress': lambda progress: self._update_progress(progress),
                'setMax': lambda max_value: self.after(0, self.log, f"Всего файлов: {max_value}")
            }

            mclib.install.install_minecraft_version(version_id, self.minecraft_dir, callback=callback)
            self.after(0, self.log, f"Версия {version_id} успешно установлена!")
            self.after(0, self.load_all_versions)
            self.after(0, self.progress_bar.set, 0)  # Сбрасываем прогресс-бар

        except Exception as e:
            self.after(0, self.log, f"Ошибка установки {version_id}: {str(e)}")
            self.after(0, self.progress_bar.set, 0)

    def _update_progress(self, progress):
        """Обновление прогресс-бара"""
        # progress - это кортеж (текущий, общий) или просто число
        if isinstance(progress, tuple) and len(progress) == 2:
            current, total = progress
            if total > 0:
                percentage = current / total
                self.progress_bar.set(percentage)
                self.after(0, self.log, f"Прогресс: {current}/{total} ({percentage * 100:.1f}%)")
        else:
            # Если progress - просто число, используем его как процент
            self.progress_bar.set(progress / 100 if progress > 1 else progress)

    def delete_version(self, version_id):
        """Удаление версии"""
        try:
            mclib.install.uninstall_version(version_id, self.minecraft_dir)
            self.log(f"Версия {version_id} удалена!")
            self.load_all_versions()
        except Exception as e:
            self.log(f"Ошибка удаления {version_id}: {str(e)}")

    def launch_game(self):
        """Запуск игры"""
        threading.Thread(target=self._launch_thread, daemon=True).start()

    def _launch_thread(self):
        version = self.version_var.get()
        if not version:
            self.log("❌ Выберите версию для запуска!")
            return

        try:
            self.after(0, self.play_button.configure, {"state": "disabled", "text": "Запуск..."})

            # Проверяем, установлена ли версия
            installed_versions = mclib.utils.get_installed_versions(self.minecraft_dir)
            version_ids = [v['id'] for v in installed_versions]

            if version not in version_ids:
                self.log(f"❌ Версия {version} не установлена!")
                self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})
                return

            options = {
                'username': 'Player',
                'uuid': '',
                'token': '',
                'jvmArguments': [
                    f"-Xmx{self.max_memory.get()}M",
                    f"-Xms{self.min_memory.get()}M"
                ]
            }

            self.log(f"🔄 Подготовка к запуску {version}...")
            command = mclib.command.get_minecraft_command(version, self.minecraft_dir, options)

            self.log("🚀 Запуск Minecraft...")
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                                       universal_newlines=True)

            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log(line.strip())

            process.stdout.close()
            process.wait()

            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})

        except Exception as e:
            self.log(f"❌ Ошибка запуска: {str(e)}")
            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})

    def log(self, message):
        """Добавление сообщения в лог"""
        self.console.insert("end", message + "\n")
        self.console.see("end")


if __name__ == "__main__":
    app = MinecraftLauncher()
    app.mainloop()
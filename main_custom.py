import customtkinter as ctk
import minecraft_launcher_lib as mclib
import subprocess
import threading
import os
import json
from PIL import Image, ImageTk
import requests
import zipfile

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
        self.custom_tab = self.tabview.add("🔧 Кастомные")
        
        self.setup_play_tab()
        self.setup_versions_tab()
        self.setup_settings_tab()
        self.setup_custom_tab()
        
        # Загрузка версий
        self.load_installed_versions()
        self.load_available_versions()
        self.load_custom_versions()

    def setup_play_tab(self):
        title_label = ctk.CTkLabel(self.play_tab, text="Minecraft Launcher", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        version_frame = ctk.CTkFrame(self.play_tab)
        version_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(version_frame, text="Выберите версию:", 
                    font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        self.version_var = ctk.StringVar()
        self.version_dropdown = ctk.CTkComboBox(version_frame, 
                                               variable=self.version_var,
                                               width=300)
        self.version_dropdown.pack(pady=10)
        
        self.play_button = ctk.CTkButton(self.play_tab, 
                                        text="🚀 Запустить Minecraft", 
                                        command=self.launch_game,
                                        height=40,
                                        font=ctk.CTkFont(size=16))
        self.play_button.pack(pady=20)
        
        console_label = ctk.CTkLabel(self.play_tab, text="Лог запуска:")
        console_label.pack(pady=(20, 5))
        
        self.console = ctk.CTkTextbox(self.play_tab, height=200)
        self.console.pack(pady=10, fill="both", expand=True)

    def setup_versions_tab(self):
        self.versions_tabview = ctk.CTkTabview(self.versions_tab)
        self.versions_tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.installed_tab = self.versions_tabview.add("Установленные")
        self.available_tab = self.versions_tabview.add("Доступные")
        
        self.installed_versions_frame = ctk.CTkScrollableFrame(self.installed_tab)
        self.installed_versions_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.available_versions_frame = ctk.CTkScrollableFrame(self.available_tab)
        self.available_versions_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        refresh_frame = ctk.CTkFrame(self.versions_tab)
        refresh_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(refresh_frame, text="Обновить список", 
                     command=self.load_all_versions).pack(side="left", padx=5)

    def setup_settings_tab(self):
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
        
        # Выбор Java
        java_frame = ctk.CTkFrame(self.settings_tab)
        java_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(java_frame, text="Путь к Java", 
                    font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        java_subframe = ctk.CTkFrame(java_frame)
        java_subframe.pack(pady=10, fill="x", padx=10)
        
        self.java_path_entry = ctk.CTkEntry(java_subframe, width=400)
        self.java_path_entry.pack(side="left", padx=5, pady=5)
        
        ctk.CTkButton(java_subframe, text="Автоопределение", 
                     command=self.auto_detect_java).pack(side="left", padx=5)
        ctk.CTkButton(java_subframe, text="Обзор", 
                     command=self.browse_java).pack(side="left", padx=5)
        
        # Автоопределяем Java при запуске
        self.auto_detect_java()
        
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
        
        ctk.CTkButton(self.settings_tab, text="Сохранить настройки",
                     command=self.save_settings).pack(pady=20)

    def setup_custom_tab(self):
        add_frame = ctk.CTkFrame(self.custom_tab)
        add_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(add_frame, text="Добавить кастомную сборку", 
                    font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        input_frame = ctk.CTkFrame(add_frame)
        input_frame.pack(pady=10, fill="x", padx=10)
        
        ctk.CTkLabel(input_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        self.custom_name = ctk.CTkEntry(input_frame, width=150)
        self.custom_name.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(input_frame, text="Путь к jar:").grid(row=0, column=2, padx=5, pady=5)
        self.custom_jar_path = ctk.CTkEntry(input_frame, width=200)
        self.custom_jar_path.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkButton(input_frame, text="Обзор", 
                     command=self.browse_jar_file).grid(row=0, column=4, padx=5, pady=5)
        
        # Поле для главного класса
        ctk.CTkLabel(input_frame, text="Главный класс:").grid(row=1, column=0, padx=5, pady=5)
        self.custom_main_class = ctk.CTkEntry(input_frame, width=150)
        self.custom_main_class.insert(0, "net.minecraft.client.main.Main")  # Стандартный главный класс
        self.custom_main_class.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkButton(input_frame, text="Автоопределить", 
                     command=self.auto_detect_main_class).grid(row=1, column=2, padx=5, pady=5)
        
        # Поле для аргументов JVM
        ctk.CTkLabel(input_frame, text="Доп. аргументы:").grid(row=2, column=0, padx=5, pady=5)
        self.custom_jvm_args = ctk.CTkEntry(input_frame, width=300)
        self.custom_jvm_args.insert(0, "-Djava.library.path=natives")
        self.custom_jvm_args.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        
        ctk.CTkButton(add_frame, text="Добавить сборку",
                     command=self.add_custom_version).pack(pady=10)
        
        self.custom_versions_frame = ctk.CTkScrollableFrame(self.custom_tab)
        self.custom_versions_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def auto_detect_java(self):
        """Автоопределение пути к Java"""
        java_path = self.find_java_executable()
        if java_path:
            self.java_path_entry.delete(0, "end")
            self.java_path_entry.insert(0, java_path)
            self.log(f"✅ Java найдена: {java_path}")
        else:
            self.log("❌ Java не найдена!")

    def browse_java(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Выберите java.exe",
            filetypes=[("Java executable", "java.exe"), ("All files", "*.*")]
        )
        if file_path:
            self.java_path_entry.delete(0, "end")
            self.java_path_entry.insert(0, file_path)

    def auto_detect_main_class(self):
        """Автоопределение главного класса из jar-файла"""
        jar_path = self.custom_jar_path.get().strip()
        if not jar_path or not os.path.exists(jar_path):
            self.log("❌ Укажите путь к jar-файлу!")
            return
        
        main_class = self.extract_main_class(jar_path)
        if main_class:
            self.custom_main_class.delete(0, "end")
            self.custom_main_class.insert(0, main_class)
            self.log(f"✅ Главный класс найден: {main_class}")
        else:
            self.log("❌ Главный класс не найден в jar-файле")

    def extract_main_class(self, jar_path):
        """Извлечение главного класса из манифеста jar-файла"""
        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                # Читаем манифест
                manifest_data = jar.read('META-INF/MANIFEST.MF').decode('utf-8')
                for line in manifest_data.splitlines():
                    if line.startswith('Main-Class:'):
                        return line.split(':', 1)[1].strip()
        except:
            pass
        return None

    def browse_jar_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Выберите jar файл",
            filetypes=[("JAR files", "*.jar"), ("All files", "*.*")]
        )
        if file_path:
            self.custom_jar_path.delete(0, "end")
            self.custom_jar_path.insert(0, file_path)
            
            name = os.path.splitext(os.path.basename(file_path))[0]
            self.custom_name.delete(0, "end")
            self.custom_name.insert(0, name)
            
            # Пытаемся определить главный класс
            main_class = self.extract_main_class(file_path)
            if main_class:
                self.custom_main_class.delete(0, "end")
                self.custom_main_class.insert(0, main_class)

    def add_custom_version(self):
        name = self.custom_name.get().strip()
        jar_path = self.custom_jar_path.get().strip()
        main_class = self.custom_main_class.get().strip()
        jvm_args = self.custom_jvm_args.get().strip()
        
        if not name or not jar_path:
            self.log("❌ Заполните название и путь к jar!")
            return
        
        if not os.path.exists(jar_path):
            self.log("❌ Файл jar не найден!")
            return
        
        if not main_class:
            self.log("⚠️ Главный класс не указан, попытка автоопределения...")
            main_class = self.extract_main_class(jar_path)
            if not main_class:
                self.log("❌ Не удалось определить главный класс!")
                return
        
        custom_versions = self.load_custom_versions_data()
        custom_versions[name] = {
            "name": name,
            "jar_path": jar_path,
            "main_class": main_class,
            "jvm_args": jvm_args,
            "type": "custom"
        }
        
        self.save_custom_versions_data(custom_versions)
        self.load_custom_versions()
        self.log(f"✅ Кастомная сборка '{name}' добавлена!")

    def load_custom_versions_data(self):
        custom_file = os.path.join(self.minecraft_dir, "custom_versions.json")
        if os.path.exists(custom_file):
            with open(custom_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_custom_versions_data(self, data):
        custom_file = os.path.join(self.minecraft_dir, "custom_versions.json")
        with open(custom_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_custom_versions(self):
        custom_versions = self.load_custom_versions_data()
        
        for widget in self.custom_versions_frame.winfo_children():
            widget.destroy()
        
        if not custom_versions:
            label = ctk.CTkLabel(self.custom_versions_frame, 
                               text="Нет кастомных сборок")
            label.pack(pady=20)
            return
        
        for version_name, version_data in custom_versions.items():
            self._create_custom_version_card(version_data)

    def _create_custom_version_card(self, version_data):
        frame = ctk.CTkFrame(self.custom_versions_frame)
        frame.pack(fill="x", pady=5, padx=5)
        
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(info_frame, text=version_data['name'], 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        ctk.CTkLabel(info_frame, text=f"Класс: {version_data.get('main_class', 'Не указан')}", 
                    text_color="gray").pack(anchor="w")
        
        ctk.CTkLabel(info_frame, text=version_data['jar_path'], 
                    text_color="gray").pack(anchor="w")
        
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(side="right", padx=5, pady=5)
        
        ctk.CTkButton(btn_frame, text="Запустить", width=80,
                     command=lambda v=version_data: self.launch_custom_version(v)).pack(side="left", padx=2)
        
        ctk.CTkButton(btn_frame, text="Удалить", width=80,
                     command=lambda v=version_data['name']: self.delete_custom_version(v)).pack(side="left", padx=2)

    def delete_custom_version(self, version_name):
        custom_versions = self.load_custom_versions_data()
        if version_name in custom_versions:
            del custom_versions[version_name]
            self.save_custom_versions_data(custom_versions)
            self.load_custom_versions()
            self.log(f"✅ Кастомная сборка '{version_name}' удалена!")

    def launch_custom_version(self, version_data):
        self.version_var.set(version_data['name'])
        self.launch_game()

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
        self.load_custom_versions()

    def load_installed_versions(self):
        threading.Thread(target=self._load_installed_versions_thread, daemon=True).start()

    def _load_installed_versions_thread(self):
        try:
            versions = mclib.utils.get_installed_versions(self.minecraft_dir)
            version_ids = [v['id'] for v in versions]
            
            custom_versions = self.load_custom_versions_data()
            for custom_name in custom_versions.keys():
                version_ids.append(custom_name)
            
            self.after(0, self._update_installed_versions, versions)
            self.after(0, self._update_version_dropdown, version_ids)
            
        except Exception as e:
            self.after(0, self.log, f"Ошибка загрузки установленных версий: {str(e)}")

    def _update_installed_versions(self, versions):
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
        threading.Thread(target=self._load_available_versions_thread, daemon=True).start()

    def _load_available_versions_thread(self):
        try:
            version_list = mclib.utils.get_version_list()
            recent_versions = version_list[:20]
            self.after(0, self._update_available_versions, recent_versions)
        except Exception as e:
            self.after(0, self.log, f"Ошибка загрузки доступных версий: {str(e)}")

    def _update_available_versions(self, versions):
        for widget in self.available_versions_frame.winfo_children():
            widget.destroy()
        
        for version in versions:
            self._create_version_card(version, self.available_versions_frame, False)

    def _create_version_card(self, version, parent, is_installed):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5, padx=5)
        
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(info_frame, text=version['id'], 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        version_type = version.get('type', 'unknown')
        color = "green" if version_type == "release" else "yellow" if version_type == "snapshot" else "gray"
        ctk.CTkLabel(info_frame, text=version_type, text_color=color).pack(anchor="w")
        
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(side="right", padx=5, pady=5)
        
        if is_installed:
            ctk.CTkButton(btn_frame, text="Удалить", width=80,
                         command=lambda v=version['id']: self.delete_version(v)).pack(side="left", padx=2)
        else:
            ctk.CTkButton(btn_frame, text="Установить", width=80,
                         command=lambda v=version['id']: self.install_version(v)).pack(side="left", padx=2)

    def _update_version_dropdown(self, version_ids):
        self.version_dropdown.configure(values=version_ids)
        if version_ids:
            self.version_var.set(version_ids[0])

    def install_version(self, version_id):
        threading.Thread(target=self._install_version_thread, args=(version_id,), daemon=True).start()

    def _install_version_thread(self, version_id):
        try:
            self.after(0, self.log, f"Начата установка версии {version_id}...")
            
            callback = {
                'setStatus': lambda status: self.after(0, self.log, f"Статус: {status}"),
                'setProgress': lambda progress: self.after(0, self.log, f"Прогресс: {progress}%"),
                'setMax': lambda max_value: None
            }
            
            mclib.install.install_minecraft_version(version_id, self.minecraft_dir, callback=callback)
            self.after(0, self.log, f"Версия {version_id} успешно установлена!")
            self.after(0, self.load_all_versions)
            
        except Exception as e:
            self.after(0, self.log, f"Ошибка установки {version_id}: {str(e)}")

    def delete_version(self, version_id):
        try:
            mclib.install.uninstall_version(version_id, self.minecraft_dir)
            self.log(f"Версия {version_id} удалена!")
            self.load_all_versions()
        except Exception as e:
            self.log(f"Ошибка удаления {version_id}: {str(e)}")

    def launch_game(self):
        threading.Thread(target=self._launch_thread, daemon=True).start()

    def _launch_thread(self):
        version = self.version_var.get()
        if not version:
            self.log("❌ Выберите версию для запуска!")
            return
        
        try:
            self.after(0, self.play_button.configure, {"state": "disabled", "text": "Запуск..."})
            
            custom_versions = self.load_custom_versions_data()
            if version in custom_versions:
                self._launch_custom_version(custom_versions[version])
            else:
                self._launch_standard_version(version)
            
        except Exception as e:
            self.log(f"❌ Ошибка запуска: {str(e)}")
            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})

    def _launch_standard_version(self, version):
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
                f"-Xms{self.min_memory.get()}M",
                "-Dfml.ignoreInvalidMinecraftCertificates=true",
                "-Dfml.ignorePatchDiscrepancies=true"
            ]
        }
        
        self.log(f"🔄 Подготовка к запуску {version}...")
        command = mclib.command.get_minecraft_command(version, self.minecraft_dir, options)
        
        self._execute_game_command(command, version)

    def _launch_custom_version(self, version_data):
        jar_path = version_data['jar_path']
        main_class = version_data.get('main_class', '')
        jvm_args = version_data.get('jvm_args', '')
        
        if not os.path.exists(jar_path):
            self.log(f"❌ Файл {jar_path} не найден!")
            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})
            return
        
        if not main_class:
            self.log("❌ Главный класс не указан!")
            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})
            return
        
        # Получаем путь к Java из настроек
        java_path = self.java_path_entry.get().strip()
        if not java_path or not os.path.exists(java_path):
            self.log("❌ Путь к Java неверный! Используйте автоопределение.")
            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})
            return
        
        # Формируем команду с правильными пробелами
        jvm_args_list = [
            f"-Xmx{self.max_memory.get()}M",
            f"-Xms{self.min_memory.get()}M"
        ]
        
        # Добавляем дополнительные аргументы JVM
        if jvm_args:
            jvm_args_list.extend(jvm_args.split())
        
        # Добавляем classpath и главный класс
        jvm_args_list.extend([
            "-cp", f'"{jar_path}"',  # Заключаем путь в кавычки на случай пробелов
            main_class
        ])
        
        # Собираем полную команду
        command = [f'"{java_path}"'] + jvm_args_list  # Заключаем java_path в кавычки
        
        # Формируем строку команды для запуска
        command_str = " ".join(command)
        
        self.log(f"🔄 Запуск кастомной сборки: {version_data['name']}")
        self.log(f"Главный класс: {main_class}")
        self.log(f"Полная команда: {command_str}")
        
        # Запускаем через shell=True для правильной обработки путей с пробелами
        self._execute_game_command_shell(command_str, version_data['name'])

    def _execute_game_command_shell(self, command_str, version_name):
        """Запуск команды через shell для правильной обработки путей с пробелами"""
        try:
            self.log(f"🚀 Запуск {version_name} через shell...")
            
            process = subprocess.Popen(
                command_str,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.minecraft_dir,  # Рабочая директория
                shell=True  # Используем shell для правильной обработки путей
            )
            
            # Читаем вывод в реальном времени
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            return_code = process.poll()
            if return_code == 0:
                self.log("✅ Игра завершена успешно")
            else:
                self.log(f"❌ Игра завершена с кодом ошибки: {return_code}")
            
            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})
            
        except Exception as e:
            self.log(f"❌ Ошибка выполнения: {str(e)}")
            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})


    def _execute_game_command(self, command, version_name):
        """Запуск команды как списка аргументов (для стандартных версий)"""
        try:
            self.log(f"🚀 Запуск {version_name}...")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.minecraft_dir
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            return_code = process.poll()
            if return_code == 0:
                self.log("✅ Игра завершена успешно")
            else:
                self.log(f"❌ Игра завершена с кодом ошибки: {return_code}")
            
            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})
            
        except Exception as e:
            self.log(f"❌ Ошибка выполнения: {str(e)}")
            self.after(0, self.play_button.configure, {"state": "normal", "text": "🚀 Запустить Minecraft"})

    def find_java_executable(self):
        """Поиск исполняемого файла Java"""
        # Проверяем JAVA_HOME
        java_home = os.getenv('JAVA_HOME')
        if java_home:
            java_path = os.path.join(java_home, 'bin', 'java.exe')
            if os.path.exists(java_path):
                return java_path
        
        # Проверяем PATH
        import shutil
        java_path = shutil.which('java')
        if java_path:
            return java_path
        
        # Стандартные пути установки Java
        common_paths = [
            "C:\\Program Files\\Java\\jre-*\\bin\\java.exe",
            "C:\\Program Files (x86)\\Java\\jre-*\\bin\\java.exe",
            "C:\\Program Files\\Java\\jdk-*\\bin\\java.exe",
            "C:\\Program Files (x86)\\Java\\jdk-*\\bin\\java.exe",
        ]
        
        for path_pattern in common_paths:
            import glob
            matches = glob.glob(path_pattern)
            if matches:
                return matches[0]
        
        return None

    def log(self, message):
        self.console.insert("end", message + "\n")
        self.console.see("end")

if __name__ == "__main__":
    app = MinecraftLauncher()
    app.mainloop()

#!/bin/bash

# Ferma lo script immediatamente se un comando fallisce
set -e

echo "==================================================="
echo "  Inizio Setup Laboratorio: AI & Robotics"
echo "==================================================="

# 1. Aggiornamento sistema e utility di base
echo -e "\n---> Aggiornamento del sistema e installazione Terminator..."
sudo apt update && sudo apt upgrade -y
# NOTA: Ho aggiunto 'rsync' qui in fondo per la copia sicura delle cartelle
sudo apt install -y terminator curl software-properties-common rsync

# 2. Configurazione di CoppeliaSim (Assumendo download manuale)
echo -e "\n---> Configurazione di CoppeliaSim..."
TAR_FILE="$HOME/Downloads/CoppeliaSim_Edu_V4_10_0_rev0_Ubuntu22_04.tar.xz"
EXTRACTED_DIR="$HOME/Downloads/CoppeliaSim_Edu_V4_10_0_rev0_Ubuntu22_04"
TARGET_DIR="$HOME/CoppeliaSim"

if [ ! -d "$TARGET_DIR" ]; then
    if [ -f "$TAR_FILE" ]; then
        echo "File scaricato trovato. Estrazione in corso (potrebbe richiedere un po')..."
        cd ~/Downloads
        tar -xf "$TAR_FILE"
        mv "$EXTRACTED_DIR" "$TARGET_DIR"
        echo "CoppeliaSim installato in $TARGET_DIR"
    else
        echo "ATTENZIONE: File $TAR_FILE non trovato!"
        echo "Assicurati di aver scaricato CoppeliaSim in Downloads. Lo script andrà avanti, ma dovrai estrarlo a mano in ~/CoppeliaSim."
    fi
else
    echo "CoppeliaSim sembra essere già presente in $TARGET_DIR."
fi

# Installazione dipendenze grafiche per Coppelia
echo "Installazione librerie di sistema per CoppeliaSim..."
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev \
liblua5.3-dev libqt5gui5 libqt5network5 libqt5widgets5 \
libqt5core5a libgl1-mesa-dev libxcb-xinerama0 libnss3

# Creazione dell'alias (solo se non esiste già)
if ! grep -q "alias coppelia=" ~/.bashrc; then
    echo "alias coppelia='~/CoppeliaSim/coppeliaSim.sh'" >> ~/.bashrc
    echo "Alias 'coppelia' aggiunto al .bashrc"
fi

# 3. Python Setup & PyTorch Hardware Check
echo -e "\n---> Configurazione librerie Python e AI..."
sudo apt install -y python3-pip pciutils
python3 -m pip install pyzmq cbor2 "numpy<2"

echo -e "\n---> Rilevamento hardware per PyTorch..."
# Controlla se c'è una scheda NVIDIA tra i componenti fisici (lspci)
if lspci | grep -i nvidia > /dev/null; then
    echo "🔥 GPU NVIDIA rilevata! Installazione PyTorch con supporto CUDA..."
    python3 -m pip install torch torchvision torchaudio
else
    echo "🐌 Nessuna GPU NVIDIA diretta rilevata (o sei in VirtualBox). Installazione PyTorch CPU-only..."
    python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Installiamo YOLO alla fine. Vedendo che PyTorch c'è già (CPU o GPU), non lo sovrascriverà.
echo "Installazione di YOLO (Ultralytics)..."
python3 -m pip install ultralytics
# 4. ROS2 Humble Setup
echo -e "\n---> Configurazione Locale per ROS2..."
sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

echo -e "\n---> Aggiunta repository ROS2..."
sudo add-apt-repository universe -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

echo -e "\n---> Installazione di ROS2 Humble e Build Tools (ci vorrà tempo!)..."
sudo apt update
sudo apt install -y ros-humble-desktop
sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-argcomplete

# Aggiunta del source di ROS2 base al bashrc
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
fi

# ---------------------------------------------------------
# 5. NUOVA PARTE: SETUP DEL WORKSPACE SUL DESKTOP
# ---------------------------------------------------------
echo -e "\n---> Configurazione del Workspace del Laboratorio sul Desktop..."
WS_DIR="$HOME/Desktop/ai-and-robotics-lab"

# Crea la cartella principale sul Desktop
mkdir -p "$WS_DIR"

# Copia le cartelle colcon_ws e scenes dalla repo scaricata al Desktop
echo "Copiando le cartelle di lavoro sul Desktop..."
if [ -d "./colcon_ws" ]; then rsync -a ./colcon_ws/ "$WS_DIR/colcon_ws/"; fi
if [ -d "./scenes" ]; then rsync -a ./scenes/ "$WS_DIR/scenes/"; fi
if [ -f "./README.md" ]; then cp ./README.md "$WS_DIR/"; fi

# Compila il workspace appena copiato
if [ -d "$WS_DIR/colcon_ws" ]; then
    echo "Compilazione dei pacchetti ROS2 (colcon build)..."
    cd "$WS_DIR/colcon_ws"
    
    # "Attiva" ROS2 nello script per poter usare colcon
    source /opt/ros/humble/setup.bash
    colcon build --symlink-install

    # Aggiunge il source specifico del workspace al .bashrc dello studente
    if ! grep -q "source $WS_DIR/colcon_ws/install/setup.bash" ~/.bashrc; then
        echo "source $WS_DIR/colcon_ws/install/setup.bash" >> ~/.bashrc
        echo "Source automatico del workspace aggiunto al .bashrc"
    fi
else
    echo "ATTENZIONE: Cartella colcon_ws non trovata."
    echo "Assicurati di eseguire lo script dall'interno della cartella scaricata da GitHub."
fi

echo "==================================================="
echo "  Installazione completata con successo! 🎉"
echo "  Il tuo ambiente di lavoro è pronto in:"
echo "  ~/Desktop/ai-and-robotics-lab"
echo "  "
echo "  IMPORTANTE: Chiudi questo terminale e aprine"
echo "  uno nuovo per rendere attivi i comandi 'coppelia'"
echo "  e poter lanciare i nodi ROS2."
echo "==================================================="
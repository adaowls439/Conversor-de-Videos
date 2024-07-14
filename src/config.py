import os

def read_config(config_file):
    default_config = {
        'MB_ALVO': 7.925,
        'ULTIMOS_SEGUNDOS': 30,
        'MAX_TENTATIVAS': 10,
        'X': 1280,
        'Y': 720,
        'FPS': 25
    }

    # Verifica se o arquivo de configuração existe
    if not os.path.exists(config_file):
        # Cria o arquivo de configuração com os valores padrão
        with open(config_file, 'w') as f:
            for key, value in default_config.items():
                f.write(f"{key} = {value}\n")

    # Lê as configurações do arquivo
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.split('=')
                config[key.strip()] = float(value.strip())

    return config

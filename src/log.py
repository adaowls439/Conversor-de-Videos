import os
from datetime import datetime

# Gera o nome do arquivo de log na inicialização da aplicação
start_time = datetime.now()
log_filename = start_time.strftime("%Y-%m-%d_%H-%M-%S.log")
log_file_path = os.path.join('logs', log_filename)

# Cria a pasta 'logs' se ela não existir
if not os.path.exists('logs'):
    os.makedirs('logs')

def create_log_file(message):
    # Gera o timestamp da mensagem
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Escreve a mensagem no arquivo de log
    with open(log_file_path, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
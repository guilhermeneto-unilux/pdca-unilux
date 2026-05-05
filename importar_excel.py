import pandas as pd
from data_manager import criar_pdca
from datetime import datetime
import sys

try:
    print("Iniciando importação...")
    df = pd.read_excel('teste_importaçao2.xlsx')
    contador = 0
    for idx, row in df.iterrows():
        # Tratar colunas com possíveis espaços nas bordas
        row_dict = {str(k).strip(): v for k, v in row.items()}
        
        nome = str(row_dict.get("Nome do PDCA", row_dict.get("Nome", ""))).strip()
        descricao = str(row_dict.get("Descrição", "")).strip()
        responsavel = str(row_dict.get("Responsável", row_dict.get("Responsavel", ""))).strip()
        prazo_raw = row_dict.get("Prazo")
        
        if not nome or nome == "nan":
            continue
            
        # Format the deadline
        if pd.notnull(prazo_raw):
            if hasattr(prazo_raw, "strftime"):
                prazo = prazo_raw.strftime("%Y-%m-%d")
            else:
                try:
                    prazo = datetime.strptime(str(prazo_raw).split()[0], "%Y-%m-%d").strftime("%Y-%m-%d")
                except:
                    prazo = datetime.now().strftime("%Y-%m-%d")
        else:
            prazo = datetime.now().strftime("%Y-%m-%d")
            
        dados_pdca = {
            "titulo": nome if nome != "nan" else "PDCA Importado",
            "classificacao": "Expansão",  
            "responsavel": responsavel if responsavel and responsavel != "nan" else "Guilherme",
            "email_responsavel": "",
            "email_gerente": "",
            "prazo": prazo,
            "planejar": {
                "descricao": descricao if descricao and descricao != "nan" else "Sem descrição.",
                "topicos": ["Avaliação do projeto"],
                "objetivo": "Importado do antigo sistema",
                "responsavel": responsavel if responsavel and responsavel != "nan" else "Guilherme",
                "prazo": prazo
            }
        }
        
        criar_pdca(dados_pdca)
        contador += 1
        print(f"PDCA '{nome}' importado com sucesso!")
        
    print(f"Total importado da nova planilha: {contador}")
except FileNotFoundError:
    print("ERRO: O arquivo 'teste_importaçao2.xlsx' não foi encontrado na pasta.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Erro na importação: {e}")

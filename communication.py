"""
Communication Module - Gerador de Mensagens WhatsApp e E-mail Personalizadas
"""

import urllib.parse
import json
from typing import Dict, List, Optional


class CommunicationEngine:
    """Motor de geração de mensagens personalizadas"""

    # Templates padrão por cluster
    TEMPLATES = {
        "Campeões": {
            "whatsapp": "Oi {nome}! 👑\n\nVocê é um VIP para a gente! Aproveita um desconto exclusivo de 15% na sua próxima compra de {oferta}.\n\nVamos lá, não nega uma pizza pra gente, né? 🍕\n\nLink: [seu_link_aqui]",
            "email": "Olá {nome},\n\nVocê é nosso cliente VIP! Aproveita o desconto exclusivo de 15% que preparamos especialmente pra você.\n\nOFERTA: {oferta}\n\nAtenciosamente,\nEquipe PizzaCRM"
        },
        "Fiéis Ticket Baixo": {
            "whatsapp": "Oi {nome}! 💚\n\nSabemos que você é um frequentador assíduo! Que tal tentar nosso novo {oferta}?\n\nTeresa aqui: {dias_sem_comprar} dias é muito tempo! Volta para a gente! 🍕",
            "email": "Olá {nome},\n\nVocê é um cliente muito querido! Temos uma oferta especial pra você: {oferta}\n\nQue tal voltar a nos visitar?\n\nAtenciosamente,\nEquipe PizzaCRM"
        },
        "Em Risco": {
            "whatsapp": "Oi {nome}! 😢\n\nFaz {dias_sem_comprar} dias que não te vemos por aqui! Sente falta da gente?\n\nTem uma surpresa esperando você: {oferta} 🎁\n\nVolta logo, tá bem?",
            "email": "Olá {nome},\n\nSentimos sua falta! Preparamos uma oferta especial pra trazer você de volta: {oferta}\n\nEsperamos vê-lo em breve!\n\nAtenciosamente,\nEquipe PizzaCRM"
        },
        "Adormecidos": {
            "whatsapp": "Oi {nome}! 👋\n\nMuito tempo sem notícias suas! Faz {dias_sem_comprar} dias que você não pede com a gente! 😢\n\nVolta com tudo! Desconto de 25% te esperando: {oferta}\n\nVamos lá, uma pizza nunca é demais! 🍕",
            "email": "Olá {nome},\n\nVocê estava desaparecido! Temos um desconto especial de 25% pra te trazer de volta.\n\nOFERTA: {oferta}\n\nNão fique longe!\n\nAtenciosamente,\nEquipe PizzaCRM"
        }
    }

    def __init__(self):
        pass

    def format_whatsapp_message(
        self,
        nome: str,
        oferta: str,
        dias_sem_comprar: int = 0,
        cluster: str = "Em Risco",
        tempo_casa: int = 0,
        template_custom: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Formata uma mensagem WhatsApp personalizada

        Retorna:
            {
                "mensagem": "Texto formatado",
                "url_whatsapp": "wa.me/55[DDD][Telefone]?text=..."
            }
        """

        # Usar template customizado ou padrão
        if template_custom:
            template = template_custom
        else:
            template = self.TEMPLATES.get(cluster, self.TEMPLATES["Em Risco"])["whatsapp"]

        # Substituir variáveis
        mensagem = template.format(
            nome=nome,
            oferta=oferta,
            dias_sem_comprar=dias_sem_comprar,
            tempo_casa=tempo_casa
        )

        return {
            "mensagem": mensagem,
            "comprimento": len(mensagem)
        }


    def generate_whatsapp_link(
        self,
        ddd: str,
        telefone: str,
        mensagem: str
    ) -> str:
        """
        Gera link wa.me com mensagem pré-preenchida

        Exemplo retorno: wa.me/5521987654321?text=Oi%20Jo%C3%A3o!
        """
        # Limpar telefone (remover caracteres não numéricos)
        telefone_clean = ''.join(filter(str.isdigit, str(telefone)))
        ddd_clean = ''.join(filter(str.isdigit, str(ddd)))

        # Validar
        if len(ddd_clean) != 2 or len(telefone_clean) != 8:
            return None

        # Montar número completo
        numero_completo = f"55{ddd_clean}{telefone_clean}"

        # URL encode da mensagem
        mensagem_encoded = urllib.parse.quote(mensagem)

        wa_link = f"https://wa.me/{numero_completo}?text={mensagem_encoded}"

        return wa_link


    def format_email_message(
        self,
        nome: str,
        oferta: str,
        cluster: str = "Em Risco",
        dias_sem_comprar: int = 0,
        tempo_casa: int = 0,
        template_custom: Optional[str] = None
    ) -> str:
        """
        Formata uma mensagem de E-mail personalizada
        """

        if template_custom:
            template = template_custom
        else:
            template = self.TEMPLATES.get(cluster, self.TEMPLATES["Em Risco"])["email"]

        mensagem = template.format(
            nome=nome,
            oferta=oferta,
            dias_sem_comprar=dias_sem_comprar,
            tempo_casa=tempo_casa
        )

        return mensagem


    def prepare_webhook_payload(
        self,
        customer_data: Dict,
        channel: str = "whatsapp"
    ) -> str:
        """
        Prepara payload JSON para envio via Webhook

        Retorna JSON string pronto para POST
        """

        payload = {
            "destinatario": {
                "nome": customer_data.get('nome'),
                "email": customer_data.get('email'),
                "ddd": customer_data.get('ddd'),
                "telefone": customer_data.get('telefone'),
            },
            "mensagem": customer_data.get('mensagem'),
            "canal": channel,
            "oferta": customer_data.get('oferta'),
            "cluster": customer_data.get('cluster'),
            "score_propensao": customer_data.get('score_propensao'),
            "timestamp": customer_data.get('timestamp'),
        }

        # Remover nulos
        payload = {k: v for k, v in payload.items() if v is not None}

        return json.dumps(payload, ensure_ascii=False, indent=2)


    def generate_campaign_summary(
        self,
        df_campaign: any,
        cluster_selecionado: str,
        canal: str = "whatsapp"
    ) -> Dict:
        """
        Gera um sumário de campanha com estatísticas
        """

        summary = {
            "cluster": cluster_selecionado,
            "canal": canal,
            "total_clientes": len(df_campaign),
            "com_contato_valido": sum(
                (df_campaign['telefone'].notna() & (df_campaign['ddd'].notna()))
                if canal == "whatsapp"
                else (df_campaign['email'].notna())
            ),
            "score_propensao_medio": df_campaign['score_propensao'].mean() if 'score_propensao' in df_campaign.columns else 0,
            "receita_potencial": df_campaign['valor'].sum() if 'valor' in df_campaign.columns else 0,
            "ofertas": df_campaign['oferta_sugerida'].value_counts().to_dict(),
        }

        return summary


    def preview_campaign(
        self,
        df_campaign: any,
        n_preview: int = 3
    ) -> List[Dict]:
        """
        Retorna preview de N mensagens da campanha
        """

        previews = []

        for idx, row in df_campaign.head(n_preview).iterrows():
            whatsapp_msg = self.format_whatsapp_message(
                nome=row.get('nome'),
                oferta=row.get('oferta_sugerida'),
                dias_sem_comprar=int(row.get('recencia', 0)),
                cluster=row.get('cluster_nome'),
                tempo_casa=int(row.get('tempo_casa', 0))
            )

            preview = {
                "cliente": row.get('nome'),
                "cluster": row.get('cluster_nome'),
                "score_propensao": round(row.get('score_propensao', 0), 1),
                "mensagem": whatsapp_msg['mensagem'],
                "comprimento": whatsapp_msg['comprimento'],
            }

            previews.append(preview)

        return previews

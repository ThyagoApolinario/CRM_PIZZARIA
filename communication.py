"""
Communication Module - Gerador de Mensagens WhatsApp e E-mail Personalizadas
Motor de blocos para geração dinâmica de templates
"""

import urllib.parse
import json
from typing import Dict, List, Optional
import hashlib


class CommunicationEngine:
    """Motor de geração de mensagens personalizadas"""

    # Blocos de frases para geração dinâmica
    BLOCOS = {
        "saudacao": {
            "Campeões": {
                "whatsapp": ["Oi {nome}! 👑", "E aí, {nome}! 🌟", "Olá {nome}!"],
                "email": ["Olá {nome},", "Oi {nome},", "Prezado(a) {nome},"]
            },
            "Fiéis Ticket Baixo": {
                "whatsapp": ["Oi {nome}! 💚", "E aí, {nome}!", "Oi {nome}!"],
                "email": ["Olá {nome},", "Oi {nome},", "Olá, {nome}!"]
            },
            "Em Risco": {
                "whatsapp": ["Oi {nome}! 😢", "Ei, {nome}!", "Oi {nome}!"],
                "email": ["Olá {nome},", "Oi {nome},", "Prezado(a) {nome},"]
            },
            "Adormecidos": {
                "whatsapp": ["Oi {nome}! 👋", "E aí, {nome}?", "Oi {nome}!"],
                "email": ["Olá {nome},", "Oi {nome},", "Prezado(a) {nome},"]
            }
        },
        "recencia": {
            "recente": {
                "whatsapp": ["Que ótimo ter você ativo!", "Feliz em ver você aqui!", "Adoramos você sempre voltando!"],
                "email": ["É sempre um prazer vê-lo com a gente!", "Seu compromisso conosco é incrível!", "Adoramos sua lealdade!"]
            },
            "medio": {
                "whatsapp": ["Faz um tempo que não te vejo", "Saudade daqui!", "Tá fazendo falta"],
                "email": ["Sentimos um pouco sua falta", "Tem dias que você não aparece", "Saudade daqui!"]
            },
            "longo": {
                "whatsapp": ["Faz {dias_sem_comprar} dias que não te vemos! 👀", "Cadê você? Faz {dias_sem_comprar} dias!", "Muito tempo sem você por aqui!"],
                "email": ["Faz um bom tempo que não nos visitava — {dias_sem_comprar} dias, para ser exato!", "Sentimos sua falta! Faz {dias_sem_comprar} dias!", "Já passaram {dias_sem_comprar} dias!"]
            },
            "muito_longo": {
                "whatsapp": ["Uau! {dias_sem_comprar} dias! Que saudade! 😢", "Nossa, {dias_sem_comprar} dias sem você!", "Isso, {dias_sem_comprar} dias, {nome}!"],
                "email": ["Está difícil acreditar que passaram {dias_sem_comprar} dias!", "Saudade demais! {dias_sem_comprar} dias, {nome}!", "Faz {dias_sem_comprar} dias, parece uma eternidade!"]
            }
        },
        "oferta": {
            "desconto": {
                "whatsapp": ["Temos {oferta} esperando por você!", "Aproveite: {oferta}", "Olha que oferta boa: {oferta}! 🎉"],
                "email": ["Preparamos uma oferta especial: {oferta}", "Temos {oferta} com seu nome", "Não deixe passar: {oferta}!"]
            },
            "brinde": {
                "whatsapp": ["Tem um presente pra você: {oferta}! 🎁", "Surprise! {oferta} te aguarda!", "Olha só que legal: {oferta}!"],
                "email": ["Temos uma surpresa: {oferta}!", "Seu brinde especial: {oferta}", "Um presente te espera: {oferta}!"]
            },
            "frete_gratis": {
                "whatsapp": ["Frete grátis na próxima: {oferta}! 🚚", "Pra você: {oferta} com frete grátis!", "Que tal {oferta} sem pagar frete?"],
                "email": ["Frete grátis em {oferta}!", "Sua próxima compra com {oferta} sai sem frete!", "Aproveite {oferta} com frete grátis!"]
            },
            "bundle": {
                "whatsapp": ["Combão especial: {oferta}! 🍕", "Que tal levar {oferta}?", "Prepare-se para {oferta}!"],
                "email": ["Temos o combo perfeito: {oferta}", "Bundle especial: {oferta}", "Conheça nosso combo {oferta}!"]
            }
        },
        "cta": {
            "whatsapp": ["Pede já!", "Não perde agora! 🔥", "Aproveita! 🍕", "Vem conosco!", "Tá esperando o quê?", "Corre que não dura!"],
            "email": ["Aproveite agora!", "Não deixe para depois!", "Faça seu pedido!", "Clique aqui e aproveite!", "Venha conosco!"]
        },
        "fechamento": {
            "whatsapp": ["Um beijo,\nEquipe PizzaCRM 🍕", "Abraços,\nSua Pizzaria 🍕", "Com amor,\nPizzaCRM 🍕", "Até logo!\nEquipe PizzaCRM"],
            "email": ["Abraços,\nEquipe PizzaCRM", "Com carinho,\nPizzaCRM", "Até em breve!\nEquipe PizzaCRM", "Atenciosamente,\nEquipe PizzaCRM"]
        }
    }

    # Templates padrão por cluster (mantidos para compatibilidade)
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

    def _detectar_nivel_recencia(self, dias: int) -> str:
        """Classifica nível de recência baseado em dias sem comprar"""
        if dias < 15:
            return "recente"
        elif dias < 45:
            return "medio"
        elif dias < 90:
            return "longo"
        else:
            return "muito_longo"

    def _detectar_tipo_oferta(self, oferta: str) -> str:
        """Detecta tipo de oferta por keywords na string"""
        oferta_lower = oferta.lower()

        if "frete" in oferta_lower or "grátis" in oferta_lower:
            return "frete_gratis"
        elif "brinde" in oferta_lower or "present" in oferta_lower:
            return "brinde"
        elif "combo" in oferta_lower or "bundle" in oferta_lower or "kit" in oferta_lower:
            return "bundle"
        else:
            return "desconto"

    def _selecionar_bloco_determinista(self, opcoes: List[str], nome_cliente: str) -> str:
        """Seleciona um bloco da lista de forma determinista baseado no nome do cliente"""
        if not opcoes:
            return ""
        hash_valor = int(hashlib.md5(nome_cliente.encode()).hexdigest(), 16)
        idx = hash_valor % len(opcoes)
        return opcoes[idx]

    def generate_dynamic_template(
        self,
        nome: str,
        cluster: str,
        dias_sem_comprar: int,
        oferta: str,
        canal: str = "whatsapp"
    ) -> str:
        """
        Gera um template dinâmico combinando blocos variáveis

        Args:
            nome: Nome do cliente (usado para seleção determinista)
            cluster: Nome do cluster (Campeões, Fiéis Ticket Baixo, Em Risco, Adormecidos)
            dias_sem_comprar: Dias desde último pedido
            oferta: Descrição da oferta
            canal: "whatsapp" ou "email"

        Returns:
            String de template pronto para usar com .format()
        """
        # Detectar contextos
        nivel_recencia = self._detectar_nivel_recencia(dias_sem_comprar)
        tipo_oferta = self._detectar_tipo_oferta(oferta)

        # Selecionar blocos de forma determinista
        saudacao = self._selecionar_bloco_determinista(
            self.BLOCOS["saudacao"].get(cluster, self.BLOCOS["saudacao"]["Em Risco"])[canal],
            nome
        )

        gancho = self._selecionar_bloco_determinista(
            self.BLOCOS["recencia"][nivel_recencia][canal],
            f"{nome}_recencia"
        )

        bloco_oferta = self._selecionar_bloco_determinista(
            self.BLOCOS["oferta"].get(tipo_oferta, self.BLOCOS["oferta"]["desconto"])[canal],
            f"{nome}_oferta"
        )

        cta = self._selecionar_bloco_determinista(
            self.BLOCOS["cta"][canal],
            f"{nome}_cta"
        )

        fechamento = self._selecionar_bloco_determinista(
            self.BLOCOS["fechamento"][canal],
            f"{nome}_fechamento"
        )

        # Montar template final
        if canal == "whatsapp":
            template = f"{saudacao}\n\n{gancho}\n\n{bloco_oferta}\n\n{cta}\n\n{fechamento}"
        else:
            # Email é mais formal
            template = f"{saudacao}\n\n{gancho} {bloco_oferta}\n\n{cta}\n\n{fechamento}"

        return template

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
        n_preview: int = 3,
        template_custom: Optional[str] = None
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
                tempo_casa=int(row.get('tempo_casa', 0)),
                template_custom=template_custom
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

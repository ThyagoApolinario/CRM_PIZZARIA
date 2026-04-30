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
        """Detecta tipo de oferta por keywords (case-insensitive)"""
        oferta_lower = oferta.lower()

        if any(word in oferta_lower for word in ["frete", "grátis", "gratis", "shipment"]):
            return "frete_gratis"
        elif any(word in oferta_lower for word in ["brinde", "present", "surpresa", "gift"]):
            return "brinde"
        elif any(word in oferta_lower for word in ["combo", "bundle", "kit", "set"]):
            return "bundle"
        elif any(word in oferta_lower for word in ["desconto", "discount", "%", "off"]):
            return "desconto"
        else:
            return "desconto"  # fallback padrão

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
        canal: str = "whatsapp",
        variáveis_custom: Optional[Dict] = None
    ) -> Dict:
        """
        Gera um template dinâmico com blocos variáveis

        Args:
            nome, cluster, dias_sem_comprar, oferta, canal: dados do cliente
            variáveis_custom: Dict com variáveis adicionais {chave: valor}

        Returns:
            Dict com 'template', 'preview', e 'metadata'
        """
        variáveis_custom = variáveis_custom or {}

        nivel_recencia = self._detectar_nivel_recencia(dias_sem_comprar)
        tipo_oferta = self._detectar_tipo_oferta(oferta)

        # Selecionar blocos
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

        # Montar template com separadores
        if canal == "whatsapp":
            template = f"{saudacao}\n\n{gancho}\n\n{bloco_oferta}\n\n{cta}\n\n{fechamento}"
        else:
            template = f"{saudacao}\n\n{gancho}\n{bloco_oferta}\n\n{cta}\n\n{fechamento}"

        # Gerar preview com substituições
        preview = self._aplicar_variaveis_ao_template(
            template, nome, dias_sem_comprar, oferta, variáveis_custom
        )

        return {
            "template": template,
            "preview": preview,
            "metadata": {
                "cluster": cluster,
                "canal": canal,
                "tipo_oferta": tipo_oferta,
                "nivel_recencia": nivel_recencia,
                "blocos_usados": {
                    "saudacao": saudacao,
                    "gancho": gancho,
                    "oferta": bloco_oferta,
                    "cta": cta,
                    "fechamento": fechamento
                }
            }
        }

    def _aplicar_variaveis_ao_template(
        self,
        template: str,
        nome: str,
        dias_sem_comprar: int,
        oferta: str,
        variáveis_custom: Optional[Dict] = None
    ) -> str:
        """Aplica variáveis ao template com tratamento de erros"""
        variáveis_custom = variáveis_custom or {}

        # Montar dicionário de substituição
        variaveis = {
            "nome": nome,
            "dias_sem_comprar": dias_sem_comprar,
            "oferta": oferta,
            **variáveis_custom
        }

        try:
            return template.format(**variaveis)
        except KeyError as e:
            # Se faltar variável, usar placeholder
            chave_faltando = str(e).strip("'")
            placeholder = f"[{chave_faltando}]"
            template_seguro = template.replace("{" + chave_faltando + "}", placeholder)
            return template_seguro.format(**{k: v for k, v in variaveis.items() if "{" + k + "}" in template_seguro})

    def format_whatsapp_message(
        self,
        nome: str,
        oferta: str,
        dias_sem_comprar: int = 0,
        cluster: str = "Em Risco",
        tempo_casa: int = 0,
        template_custom: Optional[str] = None,
        usar_dinamico: bool = False
    ) -> Dict[str, str]:
        """
        Formata uma mensagem WhatsApp personalizada

        Args:
            usar_dinamico: Se True, usa geração dinâmica de blocos
            template_custom: Template manual (sobrescreve tudo)

        Retorna:
            Dict com 'mensagem', 'comprimento', e 'metadata'
        """
        if template_custom:
            # Template manual direto
            try:
                mensagem = template_custom.format(
                    nome=nome,
                    oferta=oferta,
                    dias_sem_comprar=dias_sem_comprar,
                    tempo_casa=tempo_casa
                )
            except KeyError as e:
                # Se faltar variável, deixar placeholder
                mensagem = template_custom

            return {
                "mensagem": mensagem,
                "comprimento": len(mensagem),
                "tipo": "custom"
            }

        elif usar_dinamico:
            # Usar geração dinâmica de blocos
            resultado = self.generate_dynamic_template(
                nome=nome,
                cluster=cluster,
                dias_sem_comprar=dias_sem_comprar,
                oferta=oferta,
                canal="whatsapp",
                variáveis_custom={"tempo_casa": tempo_casa}
            )
            return {
                "mensagem": resultado["preview"],
                "comprimento": len(resultado["preview"]),
                "tipo": "dinamico",
                "metadata": resultado["metadata"]
            }

        else:
            # Usar template padrão do cluster
            template = self.TEMPLATES.get(cluster, self.TEMPLATES["Em Risco"])["whatsapp"]
            mensagem = self._aplicar_variaveis_ao_template(
                template, nome, dias_sem_comprar, oferta, {"tempo_casa": tempo_casa}
            )

            return {
                "mensagem": mensagem,
                "comprimento": len(mensagem),
                "tipo": "padrao"
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
        template_custom: Optional[str] = None,
        usar_dinamico: bool = False
    ) -> Dict[str, str]:
        """
        Formata uma mensagem de E-mail personalizada

        Args:
            usar_dinamico: Se True, usa geração dinâmica de blocos
            template_custom: Template manual

        Retorna:
            Dict com 'mensagem', 'comprimento', e 'metadata'
        """
        if template_custom:
            mensagem = self._aplicar_variaveis_ao_template(
                template_custom, nome, dias_sem_comprar, oferta, {"tempo_casa": tempo_casa}
            )
            return {
                "mensagem": mensagem,
                "comprimento": len(mensagem),
                "tipo": "custom"
            }

        elif usar_dinamico:
            resultado = self.generate_dynamic_template(
                nome=nome,
                cluster=cluster,
                dias_sem_comprar=dias_sem_comprar,
                oferta=oferta,
                canal="email",
                variáveis_custom={"tempo_casa": tempo_casa}
            )
            return {
                "mensagem": resultado["preview"],
                "comprimento": len(resultado["preview"]),
                "tipo": "dinamico",
                "metadata": resultado["metadata"]
            }

        else:
            template = self.TEMPLATES.get(cluster, self.TEMPLATES["Em Risco"])["email"]
            mensagem = self._aplicar_variaveis_ao_template(
                template, nome, dias_sem_comprar, oferta, {"tempo_casa": tempo_casa}
            )
            return {
                "mensagem": mensagem,
                "comprimento": len(mensagem),
                "tipo": "padrao"
            }


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
        template_custom: Optional[str] = None,
        usar_dinamico: bool = False
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
                template_custom=template_custom,
                usar_dinamico=usar_dinamico
            )

            preview = {
                "cliente": row.get('nome'),
                "cluster": row.get('cluster_nome'),
                "score_propensao": round(row.get('score_propensao', 0), 1),
                "mensagem": whatsapp_msg['mensagem'],
                "comprimento": whatsapp_msg['comprimento'],
                "tipo_template": whatsapp_msg.get('tipo', 'padrao')
            }

            previews.append(preview)

        return previews

    def validar_template(self, template: str, obrigatorio: List[str] = None) -> Dict:
        """
        Valida um template verificando se tem todas as variáveis necessárias

        Args:
            template: String de template
            obrigatorio: Lista de variáveis que DEVEM estar no template

        Retorna:
            Dict com 'valido', 'variaveis_faltando', 'variaveis_encontradas'
        """
        import re

        obrigatorio = obrigatorio or ["nome", "oferta"]
        variaveis_encontradas = set(re.findall(r'{(\w+)}', template))
        variaveis_faltando = set(obrigatorio) - variaveis_encontradas

        return {
            "valido": len(variaveis_faltando) == 0,
            "variaveis_encontradas": list(variaveis_encontradas),
            "variaveis_faltando": list(variaveis_faltando),
            "comprimento": len(template)
        }

    def listar_templates_disponiveis(self) -> Dict:
        """Retorna lista de todos os templates disponíveis por cluster e canal"""
        return {
            cluster: {
                "whatsapp": self.TEMPLATES[cluster]["whatsapp"][:100] + "...",
                "email": self.TEMPLATES[cluster]["email"][:100] + "..."
            }
            for cluster in self.TEMPLATES.keys()
        }

    def comparar_templates(self, templates: List[Dict]) -> Dict:
        """
        Compara múltiplos templates lado a lado

        Args:
            templates: Lista de dicts {'nome': str, 'template': str, 'nome': str, 'oferta': str, 'dias': int}

        Retorna:
            Dict com comparação e métricas
        """
        comparacao = []

        for tpl in templates:
            resultado = self.format_whatsapp_message(
                nome=tpl.get('nome', 'João'),
                oferta=tpl.get('oferta', '15% de desconto'),
                dias_sem_comprar=tpl.get('dias', 30),
                cluster=tpl.get('cluster', 'Em Risco'),
                template_custom=tpl.get('template'),
                usar_dinamico=tpl.get('dinamico', False)
            )

            validacao = self.validar_template(tpl.get('template', '')) if tpl.get('template') else None

            comparacao.append({
                "nome": tpl.get('nome_template', 'Template'),
                "comprimento": resultado['comprimento'],
                "tipo": resultado.get('tipo'),
                "preview": resultado['mensagem'][:150] + "...",
                "validacao": validacao
            })

        return {"templates": comparacao, "total": len(comparacao)}

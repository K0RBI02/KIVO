"""
KIVO Engine
Demo / Smoke-Test

Rekonstruiert genau das Szenario aus dem alten run.py:
Node A wird erstellt -> Regel erzeugt Node C -> Regel verbindet C mit B.

Zusaetzlich: ein Beweis, dass container.resolve(DomainManager) und
context.domain jetzt IDENTISCH sind (der alte Bug).
"""

from core.engine import Engine
from core.config import EngineConfig
from core.seed import Seed

from domain.node import Node
from domain.relation import Relation
from domain.manager import DomainManager
from rules.engine import Rule


engine = Engine(config=EngineConfig())
engine.initialize()
engine.start()

domain = engine.context.domain
seed = Seed(domain)

# ==================== BEWEIS: kein doppelter DomainManager mehr ====================

resolved = engine.context.container.resolve(DomainManager)
assert resolved is domain, "BUG: container liefert einen ANDEREN DomainManager als context.domain!"
print("[CHECK] container.resolve(DomainManager) is context.domain ->", resolved is domain)

# ==================== RULES ====================

def cond_a(node):
    return node.name == "A"


def action_a(node, domain):
    """Wenn Node A erkannt wird, erstelle Node C"""
    domain.add_node(Node(name="C"))


def cond_c(node):
    return node.name == "C"


def action_c(node, domain):
    """Wenn Node C erkannt wird, verbinde C -> B"""
    b = domain.get_by_name("B")
    if not b:
        return

    domain.add_relation(Relation(source_id=node.id, target_id=b.id))


engine.context.rule_engine.add_rule(Rule(cond_a, action_a, name="rule_a_creates_c"))
engine.context.rule_engine.add_rule(Rule(cond_c, action_c, name="rule_c_links_b"))

# ==================== SEED ====================

seed.node("B")  # B ZUERST erstellen!
seed.node("A")  # Dann A -> triggert C -> C sucht B -> FOUND!

# ==================== OUTPUT ====================

print("Nodes:", domain.nodes())
print("Relations:", domain.relations())
print("KIVO laeuft")

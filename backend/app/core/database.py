from neo4j import GraphDatabase, basic_auth
import os

class Database:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None

    def connect(self):
        if not self.driver:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=basic_auth(self.user, self.password)
            )

    def close(self):
        if self.driver:
            self.driver.close()
            
    def query(self, query: str, parameters: dict = None):
        if not self.driver:
            self.connect()
        # Simple auto-commit execution for now
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]
            
    def apply_constraints(self):
        """
        Apply uniqueness constraints for Risk, Control, etc.
        """
        constraints = [
            "CREATE CONSTRAINT risk_id_unique IF NOT EXISTS FOR (n:Risk) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT control_id_unique IF NOT EXISTS FOR (n:Control) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT framework_id_unique IF NOT EXISTS FOR (n:Framework) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT requirement_id_unique IF NOT EXISTS FOR (n:Requirement) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT proposal_id_unique IF NOT EXISTS FOR (n:Proposal) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT source_id_unique IF NOT EXISTS FOR (n:Source) REQUIRE n.id IS UNIQUE"
        ]
        
        if not self.driver:
            self.connect()
            
        with self.driver.session() as session:
            for constraint in constraints:
                session.run(constraint)

    def execute_write(self, query: str, params: dict = None, user: str = "system", action: str = "generic_write"):
        """
        Executes a write query and records an audit log in the same transaction.
        """
        import json
        if not self.driver:
            self.connect()
            
        params = params or {}
        params_str = json.dumps(params)
        
        audit_query = """
        CREATE (a:AuditLog {
            id: randomUUID(),
            user: $user,
            action: $action,
            payload: $payload,
            timestamp: datetime()
        })
        """
        
        def _transaction_work(tx):
            # Run the actual operation
            result = tx.run(query, params)
            data = [record.data() for record in result]
            
            # Run the audit logging
            tx.run(audit_query, user=user, action=action, payload=params_str)
            
            return data
            
        with self.driver.session() as session:
            return session.execute_write(_transaction_work)

    def execute_read(self, query: str, params: dict = None):
        """
        Executes a read-only query.
        """
        if not self.driver:
            self.connect()
            
        def _read_work(tx):
            result = tx.run(query, params)
            return [record.data() for record in result]
            
        with self.driver.session() as session:
            return session.execute_read(_read_work)

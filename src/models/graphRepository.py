class GraphRepository:
    def __init__(self, driver):
        self.driver = driver
    
    @staticmethod
    def build_set_clause(alias: str, props: dict) -> str:
        return ", ".join([f"{alias}.{k} = ${k}" for k in props.keys()])
    
    
    def clearGraph(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Graph cleared!")
        
    def save_airports(self, airports):
        with self.driver.session() as session:
            for airport in airports:
                props = airport.to_dict()
                set_clause = self.build_set_clause("a", props)

                session.run(
                    f"""
                    MERGE (a:Airport {{code: $code}})
                    SET {set_clause}
                    """,
                    **props
                )

    def save_flights(self, flights):
        with self.driver.session() as session:
            for flight in flights:
                props = flight.to_dict()
                set_clause = self.build_set_clause("r", props)

                session.run(
                    f"""
                    MATCH (o:Airport {{code: $originCode}})
                    MATCH (d:Airport {{code: $destCode}})
                    MERGE (o)-[r:FLYS_TO]->(d)
                    SET {set_clause}
                    """,
                    originCode=flight.origin.code,
                    destCode=flight.destination.code,
                    **props
                )
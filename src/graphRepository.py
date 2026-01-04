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
                    MERGE (o)-[r:FLYS_TO {{date: $date}}]->(d)
                    SET {set_clause}
                    """,
                    originCode=flight.origin.code,
                    destCode=flight.destination.code,
                    **props
                )

                
    def save_distances(self, distances):
        with self.driver.session() as session:
            for distance in distances:
                props = distance.to_dict()
                set_clause = self.build_set_clause("r", props)

                session.run(
                    f"""
                    MATCH (o:Airport {{code: $originCode}})
                    MATCH (d:Airport {{code: $destCode}})
                    MERGE (o)-[r:DISTANCE_TO]->(d)
                    SET {set_clause}
                    """,
                    originCode=distance.origin.code,
                    destCode=distance.destination.code,
                    **props
                )
                
                
    def query_flights(self, origin_airports, r1_dates, r2_dates, lengths_of_stay, blacklist_countries):
        # Construct the Cypher query with dynamic parameters for lists of dates and lengths of stay
        query = """
        MATCH path = (o1:Airport)-[r1:FLYS_TO]->(d:Airport)-[r2:FLYS_TO]->(o2:Airport)
        WHERE o1.code IN $origin_airports
            AND r1.date IN $r1_dates
            AND r2.date IN $r2_dates
            AND r2.date >= r1.date
            AND duration.between(r1.date, r2.date).days IN $lengths_of_stay  // Calculate difference in days between r1 and r2
            AND NOT d.countryName IN $blacklist_countries  // Exclude destinations in the blacklist countries
            AND o2.code IN $origin_airports
        RETURN o1.code, r1.date, d.code, r2.date, o2.code
        """

        
        # Prepare the query parameters
        params = {
            "origin_airports": origin_airports,
            "r1_dates": r1_dates,  # List of specific dates for r1
            "r2_dates": r2_dates,  # List of specific dates for r2
            "lengths_of_stay": lengths_of_stay,  # List of lengths of stay in days
            "blacklist_countries": blacklist_countries  # List of countries to blacklist
        }
        
        with self.driver.session() as session:
            result = session.run(query, params)
            return [record.data() for record in result]
from datetime import date

from src.models.airport import Airport
from src.models.neo4jResult import Neo4jResultFormatted


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
                    **props,
                )
                
    def getAirports(self) -> list[Airport]:
        with self.driver.session() as session:
            result = session.run("MATCH (a:Airport) RETURN a")
            return [Airport(**record["a"]) for record in result]

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
                    **props,
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
                    **props,
                )

    def query_flights(
            self,
            origin_departure_airports: list[str],
            origin_arrival_airports: list[str],
            r1_dates: list[date],
            r2_dates: list[date],
            lengths_of_stay: list[int],
            blacklist_countries: list[str] = None,
            whitelist_countries: list[str] = None,
            same_airport_return: bool = True,
            max_distance: int = None
        ) -> list[Neo4jResultFormatted]:
            
            # Initialize blacklist and whitelist
            blacklist_countries = blacklist_countries if blacklist_countries else []
            whitelist_countries = whitelist_countries if whitelist_countries else []
            
            base_query = """
            MATCH (o1:Airport)-[r1:FLYS_TO]->(d:Airport)-[r2:FLYS_TO]->(o2:Airport)
            WHERE o1.code IN $origin_departure_airports
                AND r1.date IN $r1_dates
                AND r2.date IN $r2_dates
                AND r2.date >= r1.date
                AND duration.between(r1.date, r2.date).days IN $lengths_of_stay
                AND o2.code IN $origin_arrival_airports
            """
            
            # Add blacklist filter only if there are countries to blacklist
            if blacklist_countries:
                base_query += "\n            AND NOT d.countryName IN $blacklist_countries"
            
            # Add whitelist filter if provided
            if whitelist_countries:
                base_query += "\n            AND d.countryName IN $whitelist_countries"
            
            # Add same airport return filter if needed
            if same_airport_return:
                base_query += "\n            AND o1.code = o2.code"
            
            base_query += """
            RETURN
                o1.code AS origin_departure_airport_code,
                r1.date AS origin_departure_date,
                d.code  AS destination_arrival_airport_code,
                d.code  AS destination_departure_airport_code,
                r2.date AS destination_departure,
                o2.code AS origin_arrival_airport_code,
                null    AS landDistance
            """
            
            distance_query = """
            MATCH (o1:Airport)-[r1:FLYS_TO]->(d1:Airport)
                -[t:DISTANCE_TO]->(d2:Airport)
                -[r2:FLYS_TO]->(o2:Airport)
            WHERE o1.code IN $origin_departure_airports
                AND r1.date IN $r1_dates
                AND r2.date IN $r2_dates
                AND r2.date >= r1.date
                AND duration.between(r1.date, r2.date).days IN $lengths_of_stay
                AND o2.code IN $origin_arrival_airports
                AND t.distance < $max_distance
            """
            
            # Add blacklist filter only if there are countries to blacklist
            if blacklist_countries:
                distance_query += "\n            AND NOT d1.countryName IN $blacklist_countries"
                distance_query += "\n            AND NOT d2.countryName IN $blacklist_countries"
            
            # Add whitelist filter if provided
            if whitelist_countries:
                distance_query += "\n            AND d1.countryName IN $whitelist_countries"
                distance_query += "\n            AND d2.countryName IN $whitelist_countries"
            
            # Add same airport return filter if needed
            if same_airport_return:
                distance_query += "\n            AND o1.code = o2.code"
            
            distance_query += """
            RETURN
                o1.code AS origin_departure_airport_code,
                r1.date AS origin_departure_date,
                d1.code AS destination_arrival_airport_code,
                d2.code AS destination_departure_airport_code,
                r2.date AS destination_departure,
                o2.code AS origin_arrival_airport_code,
                t.distance AS landDistance
            """
            
            if max_distance is not None:
                query = f"""
                {base_query}
                UNION
                {distance_query}
                """
            else:
                query = base_query
            
            params = {
                "origin_departure_airports": origin_departure_airports,
                "origin_arrival_airports": origin_arrival_airports,
                "r1_dates": r1_dates,
                "r2_dates": r2_dates,
                "lengths_of_stay": lengths_of_stay,
                "max_distance": max_distance
            }
            
            # Only add blacklist/whitelist to params if they're actually used in the query
            if blacklist_countries:
                params["blacklist_countries"] = blacklist_countries
            
            if whitelist_countries:
                params["whitelist_countries"] = whitelist_countries
            
            with self.driver.session() as session:
                result = session.run(query, params)
                return [
                    Neo4jResultFormatted(
                        origin_departure_airport_code=record["origin_departure_airport_code"],
                        destination_arrival_airport_code=record["destination_arrival_airport_code"],
                        destination_departure_airport_code=record["destination_departure_airport_code"],
                        origin_arrival_airport_code=record["origin_arrival_airport_code"],
                        origin_departure_date=record["origin_departure_date"],
                        destination_departure=record["destination_departure"],
                        travel_distance_km=record["landDistance"]
                    )
                    for record in result
                ]
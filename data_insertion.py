from neo4j import GraphDatabase

# Note in anaconda: add "neo4j+ssc" so that it works
# URI = "neo4j+ssc://1ed43e37.databases.neo4j.io"
URI = "bolt://localhost:7687"

# AUTH = ("neo4j", "PtH0CEI-e3qEhgQ6lHpKBc1eivelLLjCEIvcZwDaaO4")
AUTH = ("neo4j", "123456789")

# Paths to download from Drive (give everyone access)
# # Example: https://drive.google.com/file/d/12C5gyKKYOjVumtx0269CFaYpWCH2juNS/view?usp=drive_link
# Identify the document id ex: "12C5gyKKYOjVumtx0269CFaYpWCH2juNS"
# Download path https://drive.google.com/uc?=download&id="PUT_HERE_ID"

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    # Clear data
    driver.execute_query("MATCH (n) DETACH DELETE n")

    #Create constraints
    driver.execute_query('''
        CREATE CONSTRAINT Author_name_id IF NOT EXISTS
        FOR (a:Author) 
        REQUIRE a.name_id IS UNIQUE
    ''')

    driver.execute_query('''
        CREATE CONSTRAINT Paper_title IF NOT EXISTS
        FOR (a:Paper) 
        REQUIRE a.title IS UNIQUE
    ''')

    driver.execute_query('''
        CREATE CONSTRAINT Journal_name IF NOT EXISTS
        FOR (a:Journal) 
        REQUIRE a.name IS UNIQUE
    ''')

    driver.execute_query('''
        CREATE CONSTRAINT Volume_id IF NOT EXISTS
        FOR (a:Volume)
        REQUIRE a.id IS UNIQUE
    ''')

    driver.execute_query('''
        CREATE CONSTRAINT Volume_id IF NOT EXISTS
        FOR (a:Conference)
        REQUIRE a.title IS UNIQUE
    ''')

    driver.execute_query('''
        CREATE CONSTRAINT Volume_id IF NOT EXISTS
        FOR (a:Edition)
        REQUIRE a.title IS UNIQUE
    ''')

    driver.execute_query('''
        CREATE CONSTRAINT Volume_id IF NOT EXISTS
        FOR (a:Keyword)
        REQUIRE a.tag IS UNIQUE
    ''')

    # Load data
    # Author
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///author_node.csv' AS row 
    MERGE (a:Author {name_id: row.author_id, name: row.name, surname: row.surname}) 
                         """)

    # Papers
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///paper_node.csv' AS row 
    MERGE (:Paper {title: row.title, DOI: row.DOI, month: row.month, 
                         abstract: row.abstract}) 
                         """)

    # Journal
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///journal_node.csv' AS row 
    MERGE (:Journal {name: row.journal, main_editor: row.editor}) 
                         """)

    # Volume
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///volume_node.csv' AS row 
    MERGE (:Volume {id: row.volume, year: toInteger(row.year)})
                         """)

    # Conference
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///conference_node.csv' AS row 
    MERGE (:Conference {title: row.con_shortname})
                         """)  

    # Edition
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///edition_node.csv' AS row 
    MERGE (:Edition {title: row.edition_title
        , year: toInteger(row.edition_year)})
                         """)  

    # Keyword
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///keywords_node.csv' AS row 
    MERGE (:Keyword {tag: row.Keyword})
                         """)  
    
    # EDGES creation

    # Co-Writes edge
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///co_writes_edge.csv' AS row 
    MATCH (author:Author {name_id: row.co_author})
    MATCH (paper:Paper {title: row.paper})
    MERGE (author)-[:CO_WRITES]->(paper)
                         """) 
    
    # Writes edge
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///writes_edge.csv' AS row 
    MATCH (author:Author {name_id: row.main_author})
    MATCH (paper:Paper {title: row.paper})
    MERGE (author)-[:WRITES]->(paper)
                         """)

    # "from" edge
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///from_edge.csv' AS row
    MATCH (source:Edition {title: row.edition})
    MATCH (target:Conference {title: row.conference})
    MERGE (source)-[r: from]->(target)
                         """)
    
    # "is from" edge
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///is_from_edge.csv' AS row
    MATCH (source: Paper {title: row.paper })
    MATCH (target: Edition {title: row.edition})
    MERGE (source)-[r: is_from]->(target)
                         """) 
    
    # "published_in" edge
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///published_in_edge.csv' AS row
    MATCH (source: Paper {title: row.paper })
    MATCH (target: Volume {id: row.volume})
    MERGE (source)-[r: published_in]->(target)
                         """) 
    
    # Reviews edge
    driver.execute_query("""
    LOAD CSV WITH HEADERS FROM 'file:///reviews_edge.csv' AS row
    MATCH (author:Author {name_id: row.reviewer}), (paper:Paper {title: row.paper})
    MERGE (author)-[:REVIEWS {date: row.date}]->(paper)
                         """) 





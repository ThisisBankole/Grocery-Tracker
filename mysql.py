import pymysql
from platformshconfig import Config

def usage():
    config = Config()
    credentials = config.credentials('database')
    
    
    try:
        conn = pymysql.connect(
            host=credentials['host'],
            port=credentials['port'],
            database=credentials['path'],
            user=credentials['username'],
            password=credentials['password'])
            
        cur = conn.cursor()
            
        sql_users = '''
            
                    CREATE TABLE IF NOT EXISTS `user` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `first_name` varchar(100) NOT NULL,
                    `last_name` varchar(100) NOT NULL,
                    `email` varchar(100) NOT NULL,
                    `password` varchar(100) NOT NULL,
                    `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            
                    '''
        
        cur.execute(sql_users)
            
            
        sql_groceries = ''' 
                  
                  CREATE TABLE IF NOT EXISTS `grocery` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `user_id` int(11) NOT NULL,
                    `item` varchar(100) NOT NULL,
                    `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `quantity` int(11) DEFAULT NULL,
                    `price` float DEFAULT NULL,
                    PRIMARY KEY (`id`),
                    KEY `user_id` (`user_id`),
                    CONSTRAINT `grocery_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                  
                  
                  '''
        
        cur.execute(sql_groceries)
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(e)
        print("Database connection failed due to above error.")
        
        
        
if __name__ == '__main__':
    usage()
    
            
            
            
            
        

import traceback
class DataClient:
        def read_float_from_file(self, filename):
                
            try:
                with open("/tbu_data/"+filename, 'r') as file:
                     raw = file.read()
                     if raw != '':
                          data = float(raw)
                          return data
        
                     
                
            except FileNotFoundError:
                print("File not found.")
            except ValueError:
                traceback.print_stack()
        def read_bool_from_file(self, filename):
                
            try:
                with open("/tbu_data/"+filename, 'r') as file:
                     raw = file.read()
                     if raw != '':
                          data = int(raw)
                          return data
        
                     
                
            except FileNotFoundError:
                print("File not found.")
            except ValueError:
                traceback.print_stack()
        
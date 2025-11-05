### SRP
# BAD
class ReportService:
    def generate(self):
        print("Generating report data...")
        self._send_email()

    def _send_email(self):
        print("Emailing report...")
# GOOD
class ReportGenerator:
    def generate(self):
        print("Generating report data...")

class EmailService:
    def send(self):
        print("Sending email...")

# usage
report = ReportGenerator()
email = EmailService()
report.generate()
email.send()

### OCP
# BAD
def area(shape):
    if shape["type"] == "circle":
        return 3.14 * shape["r"]**2
    elif shape["type"] == "square":
        return shape["a"]**2

# GOOD
class Shape:
    def area(self): pass

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14 * self.r**2

class Square(Shape):
    def __init__(self, a): self.a = a
    def area(self): return self.a**2

def print_area(shape: Shape):
    print(shape.area())

### LSP
# BAD
class Bird:
    def fly(self): print("Flying high!")

class Penguin(Bird):
    def fly(self): raise Exception("Penguins can't fly!")

# GOOD
class Bird: pass

class FlyingBird(Bird):
    def fly(self): print("Flying high!")

class Penguin(Bird):
    def swim(self): print("Swimming fast!")

### ISP
# BAD
class Machine:
    def print_doc(self): pass
    def scan_doc(self): pass
    def fax_doc(self): pass

class SimplePrinter(Machine):
    def print_doc(self): print("Printing...")
    def scan_doc(self): raise NotImplementedError()
    def fax_doc(self): raise NotImplementedError()

# GOOD
class Printer:
    def print_doc(self): pass

class Scanner:
    def scan_doc(self): pass

class SimplePrinter(Printer):
    def print_doc(self): print("Printing...")

class MultiFunctionDevice(Printer, Scanner):
    def print_doc(self): print("Printing...")
    def scan_doc(self): print("Scanning...")


### DIP
# BAD
class MySQLDatabase:
    def save(self, data):
        print("Saving to MySQL")

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # tightly coupled

    def register(self, user):
        self.db.save(user)

# GOOD
class Storage:
    def save(self, data): pass

class MySQLDatabase(Storage):
    def save(self, data):
        print("Saving to MySQL")

class PostgresDatabase(Storage):
    def save(self, data):
        print("Saving to Postgres")

class FileStorage(Storage):
    def save(self, data):
        print("Saving to filesystem")

class UserService:
    def __init__(self, db: Storage):
        self.db = db  # abstraction injected

    def register(self, user):
        self.db.save(user)

# usage
service = UserService(FileStorage())
service.register("Alice")



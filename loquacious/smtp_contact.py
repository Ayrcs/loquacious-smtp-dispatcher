class SMTPContact:
    def __init__(self, name: str, email: str, data: dict | None = None):
        self.name: str = name
        self.email: str = email
        self.domain: str = email.split("@")[-1]
        self.data: dict = data or {}

    @classmethod
    def from_csv_row(cls, row: dict):
        normalized = {key.lower(): value for key, value in row.items() if key}
        email = normalized.get("email", "").strip()
        name = normalized.get("name", "").strip()

        if not email:
            raise ValueError("Contact row is missing an email value")

        data = {key: (value or "").strip() for key, value in row.items() if key}
        data.update({key.lower(): value for key, value in data.items()})
        data.setdefault("name", name)
        data.setdefault("email", email)

        return cls(name=name, email=email, data=data)

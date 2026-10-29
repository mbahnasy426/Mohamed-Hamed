"""Module 02: executable application and database data contract."""
from datetime import date
from pydantic import BaseModel, Field, field_validator, ValidationError
from sqlalchemy import (
    Column, Date, ForeignKey, Integer, Numeric, String,
    Table, MetaData, UniqueConstraint, create_engine, event
)
from sqlalchemy.schema import CreateTable
from sqlalchemy.exc import IntegrityError

class Machine(BaseModel):
    machine_id: int = Field(ge=1)
    serial_no: str = Field(min_length=3)
    site: str
    installed: date

    @field_validator("serial_no")
    @classmethod
    def serial_has_prefix(cls, value: str) -> str:
        if not value.startswith("SN-"):
            raise ValueError("serial number must start with SN-")
        return value

class MaintenanceJob(BaseModel):
    job_id: int = Field(ge=1)
    machine_id: int = Field(ge=1)
    technician: str
    done_on: date
    part_nos: list[str] = Field(default_factory=list)

metadata = MetaData()
machine_t = Table("machine", metadata,
    Column("machine_id", Integer, primary_key=True),
    Column("serial_no", String, nullable=False),
    Column("site", String, nullable=False),
    Column("installed", Date, nullable=False),
    UniqueConstraint("serial_no", name="uq_machine_serial"),
)
part_t = Table("part", metadata,
    Column("part_no", String, primary_key=True),
    Column("description", String, nullable=False),
    Column("unit_price", Numeric(9,2), nullable=False),
)
job_t = Table("maint_job", metadata,
    Column("job_id", Integer, primary_key=True),
    Column("machine_id", Integer, ForeignKey("machine.machine_id"), nullable=False),
    Column("technician", String, nullable=False),
    Column("done_on", Date, nullable=False),
)
job_part_t = Table("job_part", metadata,
    Column("job_id", Integer, ForeignKey("maint_job.job_id"), primary_key=True),
    Column("part_no", String, ForeignKey("part.part_no"), primary_key=True),
)

def main():
    engine = create_engine("sqlite:///:memory:")
    @event.listens_for(engine, "connect")
    def enable_fk(dbapi_connection, _):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    metadata.create_all(engine)
    with open(__file__.replace("contract.py","corrected-schema.sql"), "w", encoding="utf-8") as f:
        for table in metadata.sorted_tables:
            ddl = str(CreateTable(table).compile(engine)).strip()+";\n\n"
            print(ddl)
            f.write(ddl)
    # Reproducible verification: application-side validation and database-side FK
    try:
        Machine(machine_id=1, serial_no="INVALID", site="Bielefeld", installed="2026-01-01")
    except ValidationError:
        print("PASS: Pydantic rejected serial without SN- prefix")
    else:
        raise AssertionError("Pydantic check failed")
    with engine.begin() as conn:
        try:
            conn.execute(job_t.insert().values(job_id=1, machine_id=999, technician="Beier", done_on=date(2026, 1, 8)))
        except IntegrityError:
            print("PASS: SQLite foreign key rejected orphan job")
        else:
            raise AssertionError("Foreign key check failed")
    print("PASS: corrected schema created")

if __name__ == "__main__":
    main()

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config_data import config

# Собираем URL для подключения.
DATABASE_URL = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
Session = sessionmaker(bind=engine)

# Базовый класс
Base = declarative_base()


class User(Base):
    """
    Таблица пользователей.
    Храним ID Телеграма отдельно (user_id), так как он может быть очень длинным.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)

    # Связь "один ко многим"
    products = relationship("Product", back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    """
    Таблица товаров, которые мы мониторим.
    Храним две цены (текущую и старую), чтобы понимать, изменилась ли она.
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    title = Column(String)
    current_price = Column(Float)
    last_price = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))

    # Обратная связь с пользователем
    user = relationship("User", back_populates="products")



def create_db():
    """
    Создает все таблицы в базе данных, если их еще нет.
    """
    Base.metadata.create_all(engine)
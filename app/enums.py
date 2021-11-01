from enum import Enum


class CardType(Enum):
    VICTIM = "victima"
    MONSTER = "monstruo"
    ROOM = "recinto"


class VictimsNames(Enum):
    CONDE = "Conde"
    CONDESA = "Condesa"
    AMA_DE_LLAVES = "Ama de llaves"
    MAYORDOMO = "Mayordomo"
    DONCELLA = "Doncella"
    JARDINERO = "Jardinero"


class MonstersNames(Enum):
    DRACULA = "Drácula"
    FRANKENSTEIN = "Frankenstein"
    HOMBRE_LOBO = "Hombre Lobo"
    FANTASMA = "Fantasma"
    MOMIA = "Momia"
    DR_JEKYLL_MR_HYDE = "Dr. Jekyll Mr Hyde"


class RoomName(Enum):
    COCHERA = "Cochera"
    ALCOBA = "Alcoba"
    BIBLIOTECA = "Biblioteca"
    PANTEON = "Panteón"
    LABORATORIO = "Laboratorio"
    SALON = "Salon"
    BODEGA = "Bodega"
    VESTIBULO = "Vestíbulo"

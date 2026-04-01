-- 1. Crear la Base de Datos si no existe
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'BrechaDigitalDB')
BEGIN
    CREATE DATABASE BrechaDigitalDB;
END
GO

USE BrechaDigitalDB;
GO

-- 2. Tabla de Carreras (Dimensión)
CREATE TABLE Carreras (
    CarreraID INT PRIMARY KEY IDENTITY(1,1),
    NombreCarrera VARCHAR(100) NOT NULL,
    Facultad VARCHAR(100)
);

-- 3. Tabla de Estudiantes (Dimensión)
CREATE TABLE Estudiantes (
    EstudianteID INT PRIMARY KEY IDENTITY(1,1),
    Nombre VARCHAR(100) NOT NULL,
    FechaIngreso DATE,
    Genero CHAR(1),
    Ciudad VARCHAR(50)
);

-- 4. Tabla de Competencias Digitales (Nueva sugerida para BI) [cite: 58]
CREATE TABLE CompetenciasDigitales (
    CompetenciaID INT PRIMARY KEY IDENTITY(1,1),
    NombreHabilidad VARCHAR(100), -- Ej: Python, IA, Redes
    NivelRequerido VARCHAR(20) -- Básico, Intermedio, Avanzado [cite: 58]
);

-- 5. Tabla de Inscripciones e Histórico Académico (Hechos) 
CREATE TABLE Inscripciones (
    InscripcionID INT PRIMARY KEY IDENTITY(1,1),
    EstudianteID INT FOREIGN KEY REFERENCES Estudiantes(EstudianteID),
    CarreraID INT FOREIGN KEY REFERENCES Carreras(CarreraID),
    NotaFinal DECIMAL(5,2) NULL, -- Aquí irán los NULLs del 5% intencional
    SemestreActual INT
);

-- 6. Tabla de Egresados y Empleabilidad (Impacto ODS 8) [cite: 59, 61]
CREATE TABLE SeguimientoEgresados (
    EgresadoID INT PRIMARY KEY IDENTITY(1,1),
    EstudianteID INT FOREIGN KEY REFERENCES Estudiantes(EstudianteID),
    TieneEmpleoFormal BIT DEFAULT 0,
    SalarioMensualUSD DECIMAL(10,2) NULL,
    TrabajaEnAreaDeEstudio BIT DEFAULT 0
);
GO
-- hasta aqui primero luego lo de abajo

-- Insertar datos base en Carreras
INSERT INTO Carreras (NombreCarrera, Facultad) VALUES 
('Ingeniería de Sistemas', 'Ingeniería'),
('Electrónica', 'Ingeniería'),
('Administración de Empresas', 'Ciencias Económicas');

-- Bucle para generar 1000 estudiantes y sus inscripciones
DECLARE @i INT = 1;
WHILE @i <= 1000
BEGIN
    INSERT INTO Estudiantes (Nombre, FechaIngreso, Genero, Ciudad)
    VALUES ('Estudiante_' + CAST(@i AS VARCHAR), '2022-01-15', 
            CASE WHEN @i % 2 = 0 THEN 'M' ELSE 'F' END, 'Tarija');

    INSERT INTO Inscripciones (EstudianteID, CarreraID, NotaFinal, SemestreActual)
    VALUES (
        @i, 
        (ABS(CHECKSUM(NEWID())) % 3) + 1, 
        CASE WHEN @i % 20 = 0 THEN NULL ELSE (ABS(CHECKSUM(NEWID())) % 51) + 50 END, -- 5% son NULL
        (ABS(CHECKSUM(NEWID())) % 10) + 1
    );
    
    SET @i = @i + 1;
END
GO

-- Insertar datos para los primeros 500 estudiantes (suponiendo que ya egresaron)
DECLARE @j INT = 1;
WHILE @j <= 500
BEGIN
    INSERT INTO SeguimientoEgresados (EstudianteID, TieneEmpleoFormal, SalarioMensualUSD, TrabajaEnAreaDeEstudio)
    VALUES (
        @j, 
        CASE WHEN @j % 3 = 0 THEN 0 ELSE 1 END, -- Algunos desempleados para la estadística
        CASE WHEN @j % 3 = 0 THEN NULL ELSE (ABS(CHECKSUM(NEWID())) % 1000) + 500 END, 
        CASE WHEN @j % 2 = 0 THEN 1 ELSE 0 END
    );
    SET @j = @j + 1;
END
GO

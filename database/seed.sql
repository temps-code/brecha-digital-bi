-- 1. Preparar la Base de Datos
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'BrechaDigitalDB')
BEGIN
    CREATE DATABASE BrechaDigitalDB;
END
GO

USE BrechaDigitalDB;
GO

-- Eliminamos en orden inverso por las llaves foráneas
DROP TABLE IF EXISTS SeguimientoEgresados;
DROP TABLE IF EXISTS Inscripciones;
DROP TABLE IF EXISTS CompetenciasDigitales;
DROP TABLE IF EXISTS Estudiantes;
DROP TABLE IF EXISTS Carreras;
GO

-- 2. Crear Tablas (Estructura Limpia)
CREATE TABLE Carreras (
    CarreraID INT PRIMARY KEY IDENTITY(1,1),
    NombreCarrera VARCHAR(100) NOT NULL,
    Facultad VARCHAR(100)
);

CREATE TABLE Estudiantes (
    EstudianteID INT PRIMARY KEY IDENTITY(1,1),
    Nombre VARCHAR(100) NOT NULL,
    FechaIngreso DATE,
    Genero CHAR(1),
    Ciudad VARCHAR(50)
);

CREATE TABLE CompetenciasDigitales (
    CompetenciaID INT PRIMARY KEY IDENTITY(1,1),
    NombreHabilidad VARCHAR(100),
    NivelRequerido VARCHAR(20)
);

CREATE TABLE Inscripciones (
    InscripcionID INT PRIMARY KEY IDENTITY(1,1),
    EstudianteID INT FOREIGN KEY REFERENCES Estudiantes(EstudianteID),
    CarreraID INT FOREIGN KEY REFERENCES Carreras(CarreraID),
    NotaFinal DECIMAL(5,2) NULL, 
    SemestreActual INT
);

CREATE TABLE SeguimientoEgresados (
    EgresadoID INT PRIMARY KEY IDENTITY(1,1),
    EstudianteID INT FOREIGN KEY REFERENCES Estudiantes(EstudianteID),
    TieneEmpleoFormal BIT DEFAULT 0,
    SalarioMensualUSD DECIMAL(10,2) NULL,
    TrabajaEnAreaDeEstudio BIT DEFAULT 0
);
GO

-- 3. Inserción de Datos Base

-- Competencias Digitales (catálogo de habilidades TIC por nivel)
INSERT INTO CompetenciasDigitales (NombreHabilidad, NivelRequerido) VALUES
-- Básico
('Manejo de correo electrónico',     'Básico'),
('Uso de procesador de texto',       'Básico'),
('Navegación web y búsqueda',        'Básico'),
('Hojas de cálculo (Excel básico)',  'Básico'),
('Videoconferencias (Zoom, Meet)',   'Básico'),
('Gestión de archivos y carpetas',   'Básico'),
('Redes sociales profesionales',     'Básico'),
-- Intermedio
('SQL y bases de datos relacionales','Intermedio'),
('Python (scripting y análisis)',    'Intermedio'),
('Visualización de datos (Power BI)','Intermedio'),
('Excel avanzado y tablas dinámicas','Intermedio'),
('Gestión de proyectos (Jira/Trello)','Intermedio'),
('Seguridad informática básica',     'Intermedio'),
('Control de versiones (Git)',       'Intermedio'),
('Administración de redes LAN',     'Intermedio'),
-- Avanzado
('Machine Learning aplicado',        'Avanzado'),
('Arquitectura de datos en la nube', 'Avanzado'),
('Desarrollo web fullstack',         'Avanzado'),
('Ciberseguridad y ethical hacking', 'Avanzado'),
('DevOps y CI/CD',                   'Avanzado'),
('Big Data (Spark, Hadoop)',         'Avanzado'),
('Inteligencia Artificial generativa','Avanzado');
GO

INSERT INTO Carreras (NombreCarrera, Facultad) VALUES
('Ingeniería de Sistemas', 'Ingeniería'),
('Electrónica', 'Ingeniería'),
('Administración de Empresas', 'Ciencias Económicas'),
('Diseño Gráfico', 'Arquitectura y Diseño'),
('Derecho', 'Ciencias Jurídicas');

DECLARE @i INT = 1;
WHILE @i <= 50000
BEGIN
    INSERT INTO Estudiantes (Nombre, FechaIngreso, Genero, Ciudad)
    VALUES (
        'Estudiante_' + CAST(@i AS VARCHAR), 
        -- Fecha aleatoria entre 2020 y 2024
        DATEADD(DAY, ABS(CHECKSUM(NEWID())) % 1460, '2020-01-01'), 
        CASE WHEN @i % 2 = 0 THEN 'M' ELSE 'F' END, 
        -- Distribución por ciudades de Bolivia para el KPI Geográfico
        CASE ABS(CHECKSUM(NEWID())) % 5
            WHEN 0 THEN 'Tarija'
            WHEN 1 THEN 'La Paz'
            WHEN 2 THEN 'Santa Cruz'
            WHEN 3 THEN 'Cochabamba'
            ELSE 'Sucre'
        END
    );

    INSERT INTO Inscripciones (EstudianteID, CarreraID, NotaFinal, SemestreActual)
    VALUES (
        @i, 
        (ABS(CHECKSUM(NEWID())) % 5) + 1, -- Ahora elige entre las 5 carreras
        CASE WHEN @i % 20 = 0 THEN NULL ELSE (ABS(CHECKSUM(NEWID())) % 51) + 50 END, 
        (ABS(CHECKSUM(NEWID())) % 10) + 1
    );
    
    SET @i = @i + 1;
END
GO

-- Seguimiento de Egresados (Variedad en empleabilidad)
DECLARE @j INT = 1;
WHILE @j <= 25000
BEGIN
    INSERT INTO SeguimientoEgresados (EstudianteID, TieneEmpleoFormal, SalarioMensualUSD, TrabajaEnAreaDeEstudio)
    VALUES (
        @j, 
        CASE WHEN @j % 4 = 0 THEN 0 ELSE 1 END, 
        CASE WHEN @j % 4 = 0 THEN NULL ELSE (ABS(CHECKSUM(NEWID())) % 1200) + 450 END, 
        CASE WHEN @j % 2 = 0 THEN 1 ELSE 0 END
    );
    SET @j = @j + 1;
END
GO

PRINT '✅ Base de Datos BrechaDigitalDB recreada y poblada exitosamente.';
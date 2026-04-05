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
        CASE WHEN @i % 20 = 0 THEN NULL ELSE (ABS(CHECKSUM(NEWID())) % 81) + 20 END,
        (ABS(CHECKSUM(NEWID())) % 10) + 1
    );
    
    SET @i = @i + 1;
END
GO

-- Seguimiento de Egresados — patrones realistas correlacionados con carrera y ciudad
-- Tasas de empleo por carrera: Ing.Sistemas 82%, Electrónica 78%, Adm.Empresas 72%, Diseño 58%, Derecho 65%
-- Salarios: reflejan mercado boliviano real por carrera (USD)
-- TrabajaEnAreaDeEstudio: correlacionado con carrera
DECLARE @j INT = 1;
WHILE @j <= 50000
BEGIN
    DECLARE @carreraId INT;
    DECLARE @ciudad NVARCHAR(50);
    DECLARE @empleado BIT;
    DECLARE @salario DECIMAL(10,2);
    DECLARE @enArea BIT;
    DECLARE @rnd INT = ABS(CHECKSUM(NEWID())) % 100;

    -- Obtener carrera y ciudad del estudiante
    SELECT @carreraId = i.CarreraID, @ciudad = e.Ciudad
    FROM Inscripciones i JOIN Estudiantes e ON i.EstudianteID = e.EstudianteID
    WHERE i.EstudianteID = @j;

    -- Empleo: probabilidad base por carrera + ajuste por ciudad
    SET @empleado = CASE
        WHEN @carreraId = 1 AND @rnd < 82 THEN 1  -- Ing. Sistemas 82%
        WHEN @carreraId = 2 AND @rnd < 78 THEN 1  -- Electrónica 78%
        WHEN @carreraId = 3 AND @rnd < 72 THEN 1  -- Adm. Empresas 72%
        WHEN @carreraId = 4 AND @rnd < 58 THEN 1  -- Diseño Gráfico 58%
        WHEN @carreraId = 5 AND @rnd < 65 THEN 1  -- Derecho 65%
        ELSE 0
    END;

    -- Salario base por carrera, ajustado por ciudad
    SET @salario = CASE WHEN @empleado = 0 THEN NULL ELSE
        CASE @carreraId
            WHEN 1 THEN (ABS(CHECKSUM(NEWID())) % 550) + 1100  -- $1100-1650
            WHEN 2 THEN (ABS(CHECKSUM(NEWID())) % 500) + 950   -- $950-1450
            WHEN 3 THEN (ABS(CHECKSUM(NEWID())) % 450) + 750   -- $750-1200
            WHEN 4 THEN (ABS(CHECKSUM(NEWID())) % 450) + 550   -- $550-1000
            WHEN 5 THEN (ABS(CHECKSUM(NEWID())) % 550) + 700   -- $700-1250
            ELSE (ABS(CHECKSUM(NEWID())) % 800) + 600
        END *
        CASE @ciudad
            WHEN 'Santa Cruz'  THEN 1.12
            WHEN 'La Paz'      THEN 1.08
            WHEN 'Cochabamba'  THEN 1.04
            WHEN 'Tarija'      THEN 1.00
            WHEN 'Sucre'       THEN 0.95
            ELSE 1.00
        END
    END;

    -- Trabaja en área: más probable en carreras técnicas y jurídicas
    SET @enArea = CASE WHEN @empleado = 0 THEN 0 ELSE
        CASE
            WHEN @carreraId = 1 AND @rnd < 65 THEN 1  -- Ing. Sistemas 65%
            WHEN @carreraId = 2 AND @rnd < 60 THEN 1  -- Electrónica 60%
            WHEN @carreraId = 3 AND @rnd < 45 THEN 1  -- Adm. Empresas 45%
            WHEN @carreraId = 4 AND @rnd < 35 THEN 1  -- Diseño Gráfico 35%
            WHEN @carreraId = 5 AND @rnd < 70 THEN 1  -- Derecho 70%
            ELSE 0
        END
    END;

    INSERT INTO SeguimientoEgresados (EstudianteID, TieneEmpleoFormal, SalarioMensualUSD, TrabajaEnAreaDeEstudio)
    VALUES (@j, @empleado, @salario, @enArea);

    SET @j = @j + 1;
END
GO

PRINT '✅ Base de Datos BrechaDigitalDB recreada y poblada exitosamente.';
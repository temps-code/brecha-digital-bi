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
    CarreraID INT FOREIGN KEY REFERENCES Carreras(CarreraID),
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

INSERT INTO Carreras (NombreCarrera, Facultad) VALUES
('Ingeniería de Sistemas', 'Facultad de Ingeniería'),
('Ingeniería de Software', 'Facultad de Ingeniería'),
('Ciencia de Datos', 'Ciencias Exactas y Tecnología'),
('Telecomunicaciones y Redes', 'Facultad de Ingeniería'),
('Ciberseguridad', 'Ciencias Exactas y Tecnología');
GO

-- Competencias Digitales (catálogo de habilidades TIC por carrera y nivel)
-- 1: Ingeniería de Sistemas
INSERT INTO CompetenciasDigitales (CarreraID, NombreHabilidad, NivelRequerido) VALUES
(1, 'Python y Java', 'Básico'),
(1, 'SQL y bases de datos relacionales', 'Intermedio'),
(1, 'Arquitectura de Software', 'Avanzado'),
(1, 'Gestión de proyectos (Jira/Scrum)', 'Intermedio'),
(1, 'Administración de servidores Linux', 'Intermedio');

-- 2: Ingeniería de Software
INSERT INTO CompetenciasDigitales (CarreraID, NombreHabilidad, NivelRequerido) VALUES
(2, 'Control de versiones (Git)', 'Básico'),
(2, 'Desarrollo web fullstack (React/Node)', 'Avanzado'),
(2, 'Testing y QA Automatizado', 'Intermedio'),
(2, 'DevOps y CI/CD', 'Avanzado'),
(2, 'Patrones de Diseño (C#, Java)', 'Intermedio');

-- 3: Ciencia de Datos
INSERT INTO CompetenciasDigitales (CarreraID, NombreHabilidad, NivelRequerido) VALUES
(3, 'Estadística descriptiva e inferencial', 'Básico'),
(3, 'Python (pandas, numpy, scikit-learn)', 'Intermedio'),
(3, 'Machine Learning aplicado', 'Avanzado'),
(3, 'Visualización de datos (Power BI, Tableau)', 'Intermedio'),
(3, 'Big Data (Spark, Hadoop)', 'Avanzado');

-- 4: Telecomunicaciones y Redes
INSERT INTO CompetenciasDigitales (CarreraID, NombreHabilidad, NivelRequerido) VALUES
(4, 'Fundamentos de Redes (OSI, TCP/IP)', 'Básico'),
(4, 'Configuración de Routers (Cisco)', 'Intermedio'),
(4, 'Administración de redes LAN/WAN', 'Intermedio'),
(4, 'Fibra Óptica y Radioenlaces', 'Avanzado'),
(4, 'Seguridad en Redes Perimetrales', 'Avanzado');

-- 5: Ciberseguridad
INSERT INTO CompetenciasDigitales (CarreraID, NombreHabilidad, NivelRequerido) VALUES
(5, 'Seguridad informática básica', 'Básico'),
(5, 'Criptografía y Protocolos Seguros', 'Intermedio'),
(5, 'Ciberseguridad y Ethical Hacking', 'Avanzado'),
(5, 'Análisis de Vulnerabilidades y Pentesting', 'Avanzado'),
(5, 'Arquitectura de seguridad en la nube', 'Avanzado');
GO

DECLARE @i INT = 1;
WHILE @i <= 50000
BEGIN
    -- 1. Distribución realista de ciudades (Eje troncal concentra ~80%) + 5% NULLs
    DECLARE @rndCiudad INT = ABS(CHECKSUM(NEWID())) % 100;
    DECLARE @ciudad VARCHAR(50) = CASE
        WHEN @rndCiudad < 5 THEN NULL
        WHEN @rndCiudad < 35 THEN 'Santa Cruz'
        WHEN @rndCiudad < 65 THEN 'La Paz'
        WHEN @rndCiudad < 85 THEN 'Cochabamba'
        WHEN @rndCiudad < 95 THEN 'Sucre'
        ELSE 'Tarija'
    END;

    -- 2. Género con leve variación (52% F, 48% M) + 5% NULLs
    DECLARE @rndGenero INT = ABS(CHECKSUM(NEWID())) % 100;
    DECLARE @genero CHAR(1) = CASE 
        WHEN @rndGenero < 5 THEN NULL 
        WHEN @rndGenero < 54 THEN 'F' 
        ELSE 'M' 
    END;

    -- 3. Distribución realista de carreras técnicas
    DECLARE @rndCarrera INT = ABS(CHECKSUM(NEWID())) % 100;
    DECLARE @carreraId INT = CASE
        WHEN @rndCarrera < 35 THEN 1 -- Ing. Sistemas (35%)
        WHEN @rndCarrera < 60 THEN 2 -- Ing. Software (25%)
        WHEN @rndCarrera < 80 THEN 4 -- Telecomunicaciones (20%)
        WHEN @rndCarrera < 90 THEN 3 -- Ciencia de Datos (10%)
        ELSE 5                       -- Ciberseguridad (10%)
    END;

    -- 4. Semestre actual y lógica de deserción
    DECLARE @semestre INT = (ABS(CHECKSUM(NEWID())) % 10) + 1;
    DECLARE @rndDesercion INT = ABS(CHECKSUM(NEWID())) % 100;
    DECLARE @esDesercion BIT = 0;
    
    -- Mayor deserción en primeros semestres (Tasa global ~ 25%)
    IF @semestre <= 3 AND @rndDesercion < 35 SET @esDesercion = 1;
    ELSE IF @semestre <= 6 AND @rndDesercion < 15 SET @esDesercion = 1;
    ELSE IF @rndDesercion < 5 SET @esDesercion = 1;

    -- 5. Notas simulando distribución normal (Campana de Gauss) para aprobados
    DECLARE @notaFinal DECIMAL(5,2) = NULL;
    IF @esDesercion = 0
    BEGIN
        DECLARE @rndNota INT = ABS(CHECKSUM(NEWID())) % 100;
        IF @rndNota < 15 -- Reprobados (20 a 50)
            SET @notaFinal = 20 + (ABS(CHECKSUM(NEWID())) % 31);
        ELSE IF @rndNota < 60 -- Aprobados regulares (51 a 70)
            SET @notaFinal = 51 + (ABS(CHECKSUM(NEWID())) % 20);
        ELSE IF @rndNota < 85 -- Buenos (71 a 85)
            SET @notaFinal = 71 + (ABS(CHECKSUM(NEWID())) % 15);
        ELSE -- Excelentes (86 a 100)
            SET @notaFinal = 86 + (ABS(CHECKSUM(NEWID())) % 15);
    END

    INSERT INTO Estudiantes (Nombre, FechaIngreso, Genero, Ciudad)
    VALUES (
        'Estudiante_' + CAST(@i AS VARCHAR), 
        DATEADD(DAY, ABS(CHECKSUM(NEWID())) % 1460, '2020-01-01'), 
        @genero, 
        @ciudad
    );

    INSERT INTO Inscripciones (EstudianteID, CarreraID, NotaFinal, SemestreActual)
    VALUES (@i, @carreraId, @notaFinal, @semestre);
    
    SET @i = @i + 1;
END
GO

-- Seguimiento de Egresados — patrones realistas correlacionados con carrera técnica y ciudad
-- Tasas de empleo por carrera: Ing.Sistemas 82%, Ing.Software 85%, Ciencia de Datos 88%, Telecomunicaciones 75%, Ciberseguridad 90%
-- Salarios: reflejan mercado tecnológico boliviano por carrera (USD)
-- TrabajaEnAreaDeEstudio: altamente correlacionado con el rubro tecnológico
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

    -- Empleo: probabilidad base por carrera tecnológica + ajuste por ciudad
    SET @empleado = CASE
        WHEN @carreraId = 1 AND @rnd < 82 THEN 1  -- Ing. Sistemas 82%
        WHEN @carreraId = 2 AND @rnd < 85 THEN 1  -- Ing. Software 85%
        WHEN @carreraId = 3 AND @rnd < 88 THEN 1  -- Ciencia de Datos 88%
        WHEN @carreraId = 4 AND @rnd < 75 THEN 1  -- Telecomunicaciones 75%
        WHEN @carreraId = 5 AND @rnd < 90 THEN 1  -- Ciberseguridad 90%
        ELSE 0
    END;

    -- Salario base por carrera tecnológica, ajustado por ciudad
    SET @salario = CASE WHEN @empleado = 0 THEN NULL ELSE
        CASE @carreraId
            WHEN 1 THEN (ABS(CHECKSUM(NEWID())) % 550) + 1100  -- Sistemas: 100-1650
            WHEN 2 THEN (ABS(CHECKSUM(NEWID())) % 600) + 1200  -- Software: 200-1800
            WHEN 3 THEN (ABS(CHECKSUM(NEWID())) % 800) + 1500  -- Datos: 500-2300
            WHEN 4 THEN (ABS(CHECKSUM(NEWID())) % 450) + 950   -- Teleco: 50-1400
            WHEN 5 THEN (ABS(CHECKSUM(NEWID())) % 700) + 1600  -- Ciberseguridad: 600-2300
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

    -- Trabaja en área: más probable en estas carreras tecnológicas de alta demanda
    SET @enArea = CASE WHEN @empleado = 0 THEN 0 ELSE
        CASE
            WHEN @carreraId = 1 AND @rnd < 80 THEN 1  -- Ing. Sistemas 80%
            WHEN @carreraId = 2 AND @rnd < 85 THEN 1  -- Ing. Software 85%
            WHEN @carreraId = 3 AND @rnd < 90 THEN 1  -- Ciencia de Datos 90%
            WHEN @carreraId = 4 AND @rnd < 70 THEN 1  -- Telecomunicaciones 70%
            WHEN @carreraId = 5 AND @rnd < 95 THEN 1  -- Ciberseguridad 95%
            ELSE 0
        END
    END;

    INSERT INTO SeguimientoEgresados (EstudianteID, TieneEmpleoFormal, SalarioMensualUSD, TrabajaEnAreaDeEstudio)
    VALUES (@j, @empleado, @salario, @enArea);

    SET @j = @j + 1;
END
GO

PRINT '✅ Base de Datos BrechaDigitalDB recreada y poblada exitosamente.';

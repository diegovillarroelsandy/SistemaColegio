CREATE DATABASE IF NOT EXISTS SpeechTherapy;

USE SpeechTherapy;

-- Tabla que almacena la información de los usuarios
CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único del usuario
    nombre VARCHAR(100) NOT NULL,        -- Nombre del usuario
    apellido VARCHAR(50) NOT NULL,      -- Apellido del usuario
    estaActivo BOOLEAN DEFAULT TRUE,  -- a futuro para que alguien no tenga mas una cuenta
    email VARCHAR(100) UNIQUE NOT NULL,  -- Correo electrónico del usuario, debe ser único
    password VARCHAR(255) NOT NULL,      -- Contraseña del usuario almacenada de forma segura
    rol ENUM('estudiante', 'terapeuta') NOT NULL  -- Rol del usuario: puede ser estudiante o terapeuta
);

-- Tabla que almacena las acciones que pueden realizar paciente/terapeuta
-- si es terapeuta va a acciones agenda 
-- si es paciente va a tabla de comunicacion
CREATE TABLE IF NOT EXISTS accion (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único de la acción
    src VARCHAR(250) NOT NULL,          -- Ruta de la imagen o recurso asociado a la acción
    nombre VARCHAR(100) NOT NULL,       -- Nombre descriptivo de la acción
    tipo ENUM('paciente', 'terapeuta'), -- Tipo de acción, indica si es para estudiante o terapeuta
    usuario_id INT,                     -- Referencia al usuario que creó la acción (opcional)
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) -- Llave foránea que referencia a la tabla usuario
);

-- Tabla que almacena la descripción de la agenda para cada usuario
CREATE TABLE IF NOT EXISTS agenda (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único de la agenda
    descripcion VARCHAR(255) NOT NULL,  -- Descripción de la agenda
    usuario_id INT,                     -- Referencia al usuario que creó la agenda
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) -- Llave foránea que referencia a la tabla usuario
);

-- Tabla intermedia que relaciona las agendas con las acciones 
-- en diferentes periodos del día (mañana, tarde, noche)
CREATE TABLE IF NOT EXISTS agenda_accion (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único de la relación agenda-acción
    agenda_id INT,                      -- Referencia a la agenda
    accion_id INT,                      -- Referencia a la acción
    periodo ENUM('mañana', 'tarde', 'noche') NOT NULL, -- Periodo del día al que pertenece la acción
    FOREIGN KEY (agenda_id) REFERENCES agenda(id) ON DELETE CASCADE, -- Llave foránea que referencia a la tabla agenda, se elimina en cascada
    FOREIGN KEY (accion_id) REFERENCES accion(id) ON DELETE CASCADE  -- Llave foránea que referencia a la tabla acción, se elimina en cascada
);


-- Tabla para el juego discriminacion de imagenes
-- Tabla que almacena las imágenes utilizadas en el juego de discriminación de imágenes
CREATE TABLE IF NOT EXISTS imagenDiscriminacion (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único para cada imagen en el juego
    src VARCHAR(250) NOT NULL,           -- Ruta del archivo de imagen asociado, que se utilizará en el juego
    alt VARCHAR(100) NOT NULL,           -- Texto alternativo para la imagen, describe lo que representa la imagen
    esCorrecto BOOLEAN DEFAULT FALSE     -- Indica si la imagen es la respuesta correcta en el contexto del juego (true) o no (false)
);


-- Tabla para el juego de formar oraciones simples y compuestas
-- Tabla que almacena la información de las imágenes utilizadas para formar oraciones
CREATE TABLE IF NOT EXISTS sentencia (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único para cada sentencia
    src VARCHAR(250) NOT NULL,           -- Ruta del archivo de imagen asociado a la sentencia
    alt VARCHAR(100) NOT NULL,           -- Texto alternativo para la imagen, describe la sentencia
    esPronombre BOOLEAN,                 -- Indica si la imagen representa un pronombre (true) o no (false)
    esSimple BOOLEAN                     -- Indica si la imagen pertenece a una oración simple (true) o compuesta (false)
);

-- Tabla para almacenar imágenes relacionadas con emociones para juegos de reconocimiento de emociones
CREATE TABLE IF NOT EXISTS emocion (
    id INT AUTO_INCREMENT PRIMARY KEY,   -- Identificador único para cada imagen/emoción
    src VARCHAR(250) NOT NULL,           -- Ruta de la imagen que representa la emoción o un elemento relacionado
    alt VARCHAR(100) NOT NULL,           -- Texto alternativo para describir la imagen
    nombre VARCHAR(50) NOT NULL,         -- Nombre descriptivo de la emoción o del elemento relacionado
    emocion VARCHAR(50) NOT NULL,        -- Nombre de la emoción específica que la imagen representa (ej. "Felicidad", "Tristeza")
    esEmocion BOOLEAN DEFAULT TRUE,      -- Indicador de si la imagen representa una emoción (TRUE) o un elemento relacionado para reconocer la emoción (FALSE)
    esReal BOOLEAN DEFAULT TRUE          -- Indicador de si la imagen es una foto real (TRUE) o una representación gráfica (FALSE)
);


-- Actividades Lúdicas
-- Juego Intrusos
-- Tabla para almacenar los casos de intrusos
CREATE TABLE IF NOT EXISTS intruso_caso (
    id INT AUTO_INCREMENT PRIMARY KEY,    -- Identificador único para cada caso
    nombre VARCHAR(100) NOT NULL,          -- Nombre o descripción del caso
    cantidad_imagenes INT NOT NULL         -- Cantidad de imágenes en el caso (por ejemplo, 3 para nivel 1)
);

-- Tabla para almacenar las imágenes de cada caso
CREATE TABLE IF NOT EXISTS intruso_imagen (
    id INT AUTO_INCREMENT PRIMARY KEY,      -- Identificador único para cada imagen
    src VARCHAR(250) NOT NULL,              -- Ruta o URL de la imagen
    isIntruder BOOLEAN DEFAULT FALSE,       -- Identifica si la imagen es la intrusa
    caso_id INT,                            -- Referencia al caso al que pertenece la imagen
    FOREIGN KEY (caso_id) REFERENCES intruso_caso(id) ON DELETE CASCADE
);

-- Juego Colores
-- Tabla para almacenar los colores disponibles en el juego
CREATE TABLE IF NOT EXISTS color (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único del color
    nombre VARCHAR(50) NOT NULL,        -- Nombre del color (ej. "Rojo", "Verde")
    src VARCHAR(250) NOT NULL           -- Ruta o URL de la imagen que representa el color
);

-- Tabla para almacenar las imágenes que necesitan ser coloreadas
CREATE TABLE IF NOT EXISTS imagen (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único de la imagen
    src VARCHAR(250) NOT NULL,          -- Ruta o URL de la imagen
    color_correcto_id INT NOT NULL,     -- Identificador del color correcto para esta imagen
    FOREIGN KEY (color_correcto_id) REFERENCES color(id) -- Relación con la tabla de colores
);


-- Juego Rutinas
-- Tabla para almacenar las rutinas
CREATE TABLE IF NOT EXISTS routines (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único de la rutina
    nombre VARCHAR(100) NOT NULL        -- Nombre de la rutina (ej. "Dormir", "Levantarse")
);

-- Tabla para almacenar los pasos de cada rutina
CREATE TABLE IF NOT EXISTS routine_steps (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único del paso de rutina
    routine_id INT NOT NULL,            -- Identificador de la rutina asociada
    descripcion VARCHAR(255) NOT NULL,  -- Descripción o nombre del paso (ej. "Cepillar dientes")
    orden INT NOT NULL,                 -- Orden en que debe realizarse este paso dentro de la rutina
    src VARCHAR(250) NOT NULL,          -- Ruta o URL de la imagen que representa el paso
    FOREIGN KEY (routine_id) REFERENCES routines(id) ON DELETE CASCADE  -- Relación con la tabla de rutinas
);



-- Juego Sentidos
-- Tabla que almacena los diferentes sentidos
CREATE TABLE IF NOT EXISTS senses (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único para cada sentido
    src VARCHAR(250) NOT NULL,          -- Ruta de la imagen que representa el sentido
    matched BOOLEAN DEFAULT FALSE       -- Indica si el sentido ha sido emparejado correctamente en el juego
);

-- Tabla que almacena las figuras asociadas a los sentidos
CREATE TABLE IF NOT EXISTS figuras (
    id INT AUTO_INCREMENT PRIMARY KEY,   -- Identificador único para cada figura
    src VARCHAR(250) NOT NULL,           -- Ruta de la imagen que representa la figura relacionada con el sentido
    matched BOOLEAN DEFAULT FALSE,       -- Indica si la figura ha sido emparejada correctamente en el juego
    senses_id INT,                       -- Relación con el sentido correspondiente (identificador de la tabla `senses`)
    FOREIGN KEY (senses_id) REFERENCES senses(id) -- Clave foránea que relaciona la figura con un sentido específico
);


-- Juego para Figuras
-- Tabla para almacenar tanto figuras geométricas como imágenes relacionadas con esas figuras
CREATE TABLE IF NOT EXISTS figura (
    id INT AUTO_INCREMENT PRIMARY KEY,                      -- Identificador único para cada entrada en la tabla
    src VARCHAR(250) NOT NULL,                              -- Ruta de la imagen para la figura o imagen relacionada
    alt VARCHAR(100) NOT NULL,                              -- Texto alternativo para describir la figura o imagen
    figura ENUM('circulo', 'cuadrado', 'triangulo') NOT NULL, -- Tipo de figura geométrica
    esFiguraBase BOOLEAN DEFAULT TRUE                       -- Indica si es una figura geométrica básica (true) o una imagen relacionada (false)
);



-- Juego de Siluetas
-- Tabla que almacena las diferentes siluetas
CREATE TABLE IF NOT EXISTS siluetas (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único para cada silueta
    src VARCHAR(250) NOT NULL,          -- Ruta de la imagen que representa la silueta
    matched BOOLEAN DEFAULT FALSE       -- Indica si la silueta ha sido emparejada correctamente en el juego
);

-- Tabla que almacena las fotos asociadas a las siluetas
CREATE TABLE IF NOT EXISTS fotos_siluetas (
    id INT AUTO_INCREMENT PRIMARY KEY,   -- Identificador único para cada foto
    src VARCHAR(250) NOT NULL,           -- Ruta de la imagen que representa la foto relacionada con la silueta
    matched BOOLEAN DEFAULT FALSE,       -- Indica si la foto ha sido emparejada correctamente en el juego
    silueta_id INT,                      -- Relación con la silueta correspondiente (identificador de la tabla `siluetas`)
    FOREIGN KEY (silueta_id) REFERENCES siluetas(id) -- Clave foránea que relaciona la foto con una silueta específica
);


-- Juego Situaciones
-- Tabla que almacena las situaciones
CREATE TABLE IF NOT EXISTS situaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único para cada situación
    src VARCHAR(250) NOT NULL,          -- Ruta de la imagen que representa la situación
    descripcion VARCHAR(255) NOT NULL   -- Descripción de la situación (opcional, para mayor contexto)
);

-- Tabla que almacena las opciones de imágenes asociadas a cada situación
CREATE TABLE IF NOT EXISTS opciones_situacion (
    id INT AUTO_INCREMENT PRIMARY KEY,    -- Identificador único para cada opción de imagen
    src VARCHAR(250) NOT NULL,            -- Ruta de la imagen que representa la opción
    esCorrecta BOOLEAN NOT NULL,          -- Indica si la imagen es la respuesta correcta para la situación
    situacion_id INT,                     -- Relación con la situación correspondiente (identificador de la tabla `situaciones`)
    FOREIGN KEY (situacion_id) REFERENCES situaciones(id) ON DELETE CASCADE -- Clave foránea que relaciona la opción con una situación específica
);

-- Tabla Reporte
CREATE TABLE IF NOT EXISTS reportes (
    id INT AUTO_INCREMENT PRIMARY KEY,           -- Identificador único para cada reporte
    usuario_id INT NOT NULL,                     -- Relación con el usuario que realizó el juego
    juego ENUM('discriminacion', 'oraciones', 'emociones', 'intrusos', 'colores', 'rutinas', 'sentidos', 'figuras', 'siluetas', 'situaciones') NOT NULL,                                        -- Nombre del juego realizado
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,    -- Fecha y hora en la que se realizó el juego
    aciertos INT DEFAULT 0,                      -- Número de respuestas correctas
    incorrectos INT DEFAULT 0,                   -- Número de respuestas incorrectas
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE -- Clave foránea que relaciona el reporte con un usuario específico
);

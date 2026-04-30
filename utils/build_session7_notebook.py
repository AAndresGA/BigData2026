from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header, toc, section_header


def build_cells():
    cells = [
        *uce_header(
            title="Spark en Databricks: de Pandas y Dask a Big Data operativo",
            session=8,
            github_path="main/Cuadernos/7_Hadoop_YARN_Spark_Databricks.ipynb",
            nota_plataforma=(
                "Databricks Community Edition. El notebook esta pensado para ejecutarse "
                "alli; Colab solo sirve para lectura parcial."
            ),
        ),
        md(
            """
            ## Proposito pedagogico

            Esta sesion marca el paso natural despues de **Pandas** y **Dask**. El objetivo no es
            solo aprender una API nueva, sino entender **cuando Spark vale la pena**, como se conecta
            con ideas de **Hadoop** y **YARN**, y por que herramientas como **Databricks** y
            **Delta Lake** aparecen tan seguido en entornos Big Data reales.

            ### Al final de la sesion deberias poder:
            - Explicar por que Spark aparece como el siguiente paso despues de Pandas y Dask.
            - Explicar por que **Pandas**, **Dask** y **PySpark** resuelven problemas distintos.
            - Describir el papel de **HDFS**, **YARN** y **Spark** dentro del ecosistema Hadoop.
            - Reconocer el costo de los **shuffles**, de las **Python UDFs** y de mover datos al driver.
            - Usar Databricks como laboratorio para inspeccionar **Jobs, Stages y Tasks**.
            - Entender por que **Delta Lake** es una ventaja operativa y no solo un formato mas.
            - Resolver un mini taller sin caer en anti-patrones comunes.
            """
        ),
        toc(
            [
                "0. Crear cuenta en Databricks y conocer la plataforma",
                "1. Por que Spark y por que Databricks",
                "2. Hadoop, YARN y el lugar de Spark",
                "3. Preparacion del entorno y dataset",
                "4. Modelo mental de Spark",
                "5. Que puede salir mal",
                "6. Spark SQL como puente para analitica",
                "7. Pandas vs Dask vs PySpark",
                "8. Delta Lake en la practica",
                "9. Taller guiado",
                "10. Checklist final de produccion",
            ]
        ),
        section_header("0", "Crear cuenta en Databricks y conocer la plataforma"),
        md(
            """
            ## Crear tu cuenta en Databricks Community Edition

            Si nunca has usado Databricks, sigue estos pasos antes de arrancar el laboratorio:

            1. Ve a **https://community.cloud.databricks.com/**.
            2. Registrate con tu correo.
            3. Crea un workspace personal si la plataforma lo solicita.
            4. Una vez dentro, identifica estas tres areas:
               - **Workspace**: donde viven notebooks, carpetas y repos.
               - **Compute**: donde creas y administras clusters.
               - **Data**: donde exploras tablas, volumenes y catalogos segun el entorno.

            ## Introduccion corta a la plataforma

            Este notebook esta escrito para **Databricks Community Edition** y asume un cluster
            **Single Node**. Eso significa que:

            - Es excelente para aprender la API y la UI de Spark.
            - No representa un cluster multinodo real.
            - Algunos benchmarks favorecen menos a Spark de lo que ocurriria en produccion.
            - DBFS en Community Edition puede ser temporal; si recreas el cluster tal vez debas descargar de nuevo.

            > Regla de lectura: si una celda dice **observa la Spark UI**, no la saltes. Parte de aprender Spark
            > es entender **como ejecuta**, no solo **que resultado produce**.
            """
        ),
        md(
            """
            ## Recorrido minimo por la interfaz

            Antes de escribir codigo, ubica mentalmente estos conceptos:

            - **Notebook**: interfaz interactiva donde escribes Python, SQL y Markdown.
            - **Cluster**: el recurso de computo que ejecuta Spark.
            - **DBFS**: capa de archivos accesible desde Spark y desde utilidades de Databricks.
            - **Spark UI**: panel para inspeccionar jobs, stages, tasks y plan de ejecucion.

            Para esta sesion, crea un cluster con una configuracion simple:

            - **Cluster mode**: `Single Node`
            - **Runtime**: una version LTS reciente de Databricks Runtime
            - **Auto termination**: 30-60 minutos si quieres ahorrar recursos

            > Importante: aunque Community Edition se llame "cluster", en esta modalidad no estamos
            > simulando un entorno multinodo completo. Lo usamos porque reduce friccion y permite
            > aprender Spark con menos problemas operativos que Colab.
            """
        ),
        md(
            """
            ## Que es un cluster y que significa `Single Node`

            Antes de avanzar, conviene aclarar una palabra que aparece todo el tiempo en Spark:
            **cluster**.

            Un **cluster** es un conjunto de maquinas que trabajan juntas para ejecutar tareas y procesar datos.
            En Spark, la idea general es que el trabajo no lo haga una sola maquina aislada, sino varias maquinas
            coordinadas:

            - una coordina el trabajo,
            - otras ejecutan tareas,
            - y entre todas procesan mas datos y mas rapido que una sola maquina.

            Un **nodo** es simplemente una maquina dentro de ese sistema.

            En Spark, un cluster normalmente tiene:

            - **Driver**: coordina el trabajo, construye el plan de ejecucion y reparte tareas.
            - **Executors**: ejecutan las tareas y procesan los datos.
            - **Cluster manager**: administra recursos y decide donde corre cada cosa.

            ### Entonces, que significa `Single Node`?

            `Single Node` significa que todo corre en **una sola maquina**.

            Es decir:

            - el driver esta en esa maquina,
            - los executors tambien,
            - no hay varias maquinas repartiendo el trabajo de verdad.

            Sigue siendo Spark, pero no es un cluster distribuido real entre varios nodos.

            ### Por que usar `Single Node` entonces?

            Porque sirve muy bien para:

            - aprender la API de Spark,
            - practicar `DataFrame`, `groupBy`, `join`, `sql`,
            - ver jobs, stages y tasks,
            - usar Databricks con menos complejidad,
            - reducir costos y friccion.

            ### Que pierde frente a un cluster real?

            Pierde sobre todo:

            - escalamiento real entre varias maquinas,
            - comportamiento de red entre nodos,
            - distribucion fisica autentica,
            - ventajas completas de paralelismo multinodo.

            > Idea clave: `Single Node` no reemplaza un cluster real, pero si es un muy buen laboratorio para aprender Spark.
            """
        ),
        md(
            """
            ## Databricks Community Edition no es solo otro Colab

            A primera vista, Databricks Community Edition puede parecerse a Colab porque ambos son:

            - notebooks en la nube,
            - interactivos,
            - comodos para ensenar,
            - sin demasiada instalacion local.

            Pero pedagogicamente no cumplen el mismo papel.

            ### Colab

            Colab esta pensado como un entorno general para:

            - Python,
            - notebooks,
            - ML basico,
            - Pandas,
            - visualizacion,
            - prototipos rapidos.

            Spark en Colab normalmente:

            - no es la experiencia nativa,
            - suele correr en modo local o semiartesanal,
            - no ensena tan bien la logica operacional de Spark,
            - no esta centrado en jobs, stages, tasks, storage, tablas ni Delta.

            ### Databricks Community Edition

            Databricks Community Edition esta pensado especificamente para:

            - Spark,
            - Spark SQL,
            - notebooks de datos,
            - tablas,
            - DBFS,
            - Delta Lake,
            - observabilidad con Spark UI.

            Aunque Community Edition sea limitado, se diferencia de Colab en que:

            - **Spark es ciudadano de primera clase**,
            - el entorno esta disenado alrededor del motor,
            - la UI y el flujo de trabajo ensenan mejor como se usa Spark en la practica,
            - se parece mas al mundo real de data engineering.

            ### Entonces, se parece a Colab?

            Si, en la experiencia superficial.

            Abres navegador, ejecutas celdas y trabajas en un notebook. En eso si se parecen.
            Pero la diferencia profunda es esta:

            - **Colab** ensena "programar y analizar".
            - **Databricks** ensena mejor "trabajar con un motor de datos distribuido".

            Colab es un muy buen cuaderno de laboratorio general.
            Databricks Community Edition es un laboratorio mas especifico para Spark.

            ### Lo importante para esta sesion

            - Community Edition **no es produccion**.
            - Community Edition **no reemplaza un cluster real multinodo**.
            - Pero tampoco es simplemente "un Colab con otro nombre".
            - Es una plataforma de aprendizaje donde Spark, SQL, storage y observabilidad estan mucho mas integrados.
            """
        ),
        code(
            """
            # Verificacion del entorno de Databricks
            import sys

            print(f"Python: {sys.version}")
            print(f"Spark:  {spark.version}")
            print(f"Master: {spark.sparkContext.master}")
            print(f"App:    {spark.sparkContext.appName}")
            print(f"UI:     {spark.sparkContext.uiWebUrl}")

            try:
                root_items = dbutils.fs.ls("/")
                print(f"\\nDBFS disponible: {len(root_items)} entradas en /")
            except NameError as exc:
                raise RuntimeError(
                    "Este notebook esta pensado para Databricks. "
                    "dbutils no esta disponible en este entorno."
                ) from exc
            """
        ),
        code(
            """
            # Dependencias adicionales para la comparacion con Dask
            # Usamos %pip y no %sh pip install para que el paquete quede disponible
            # en el interprete del notebook.
            %pip install "dask[dataframe]>=2024.1" pyarrow -q
            """
        ),
        md(
            """
            ## Regla importante sobre `%pip`

            En Databricks, instalar librerias con `%sh pip install ...` es un error frecuente:
            el paquete puede quedar en el sistema, pero **no necesariamente en la sesion Python activa**.

            Usa `%pip` para notebooks interactivos. Si una instalacion exige reinicio del interprete,
            Databricks te lo indicara.
            """
        ),
        section_header("1", "Por que Spark y por que Databricks"),
        md(
            """
            ## La pregunta correcta no es "cual es mejor"

            La pregunta correcta es: **que herramienta minimiza costo, tiempo y riesgo para este problema**.

            | Herramienta | Gana cuando... | Pierde cuando... |
            |---|---|---|
            | **Pandas** | los datos caben bien en memoria, iteras rapido, exploras localmente | el dataset crece y el driver se ahoga |
            | **Dask** | quieres escalar una API parecida a Pandas con esfuerzo moderado | necesitas optimizacion de joins/shuffles muy robusta o ecosistema de produccion mas maduro |
            | **Spark** | hay volumen grande, pipelines repetibles, SQL distribuido, joins pesados, observabilidad operativa | el problema es pequeno y el overhead distribuido no compensa |

            ### Por que Databricks ayuda a aprender Spark
            - Ya trae `spark` configurado.
            - Expone muy bien la **Spark UI**.
            - Facilita trabajar con **Delta Lake**.
            - Reduce friccion operativa para centrar la clase en el modelo mental.

            ### Honestidad pedagogica
            Community Edition es un gran laboratorio, pero **no sustituye** un cluster multinodo real.
            Aqui aprenderemos conceptos y patrones; el rendimiento absoluto no siempre es representativo.
            """
        ),
        md(
            """
            ## Casos donde Spark SI vale la pena

            - Un `join` entre tablas grandes donde mover todo al driver seria inviable.
            - ETLs programados que deben ser reproducibles y observables.
            - Transformaciones SQL repetitivas sobre particiones de datos grandes.
            - Feature engineering distribuido para ML.
            - Tablas transaccionales con historico, rollback y upserts usando Delta Lake.

            ## Casos donde NO deberias empezar con Spark

            - Tienes 200 MB y una laptop con 32 GB RAM.
            - Necesitas prototipar analisis exploratorio muy rapido.
            - La mayor parte del trabajo es visualizacion local o limpieza manual.
            - Tu equipo domina Pandas y el cuello de botella aun no es computacional.
            """
        ),
        section_header("2", "Hadoop, YARN y el lugar de Spark"),
        md(
            """
            ## Del ecosistema Hadoop a Spark

            Antes de Spark, el mundo Big Data ya tenia una forma de trabajar con datos grandes: **Hadoop**.

            Pero Hadoop no era "una sola herramienta". En realidad, era un ecosistema de componentes pensado
            para resolver una pregunta muy concreta:

            > "Si mis datos ya no caben en una sola maquina, como los guardo, como los proceso y como organizo los recursos para hacerlo?"

            Para responder esa pregunta, conviene separar tres piezas clave:

            - **HDFS**: almacenamiento distribuido para archivos grandes.
            - **MapReduce**: modelo de computacion distribuida clasico de Hadoop.
            - **YARN**: capa de administracion de recursos y ejecucion de aplicaciones.

            Si entiendes que hacia cada una, entiendes mucho mejor por que Spark aparecio despues y por que tuvo tanta adopcion.

            ---

            ## 1. HDFS: donde viven los datos

            **HDFS** significa **Hadoop Distributed File System**.
            Su funcion principal es el **almacenamiento distribuido**.

            En lugar de guardar un archivo gigantesco en una sola maquina, HDFS:

            - divide el archivo en bloques,
            - reparte esos bloques entre varias maquinas,
            - y guarda copias para tolerar fallos.

            Eso significa que un archivo muy grande no vive completo en un solo disco, sino repartido en varias partes del cluster.

            ### Por que eso era importante?

            Porque en Big Data el primer problema no es solo "procesar mucho", sino **guardar mucho de forma confiable**.
            Si una maquina falla, no quieres perder todos los datos.

            ### Idea clave

            - **HDFS no procesa datos**
            - **HDFS almacena datos**

            > **HDFS = sistema de archivos distribuido**

            ---

            ## 2. MapReduce: como se procesaban esos datos

            Una vez que los datos estaban almacenados en HDFS, hacia falta procesarlos.
            Ahi entra **MapReduce**, que fue el modelo clasico de computacion de Hadoop.

            La idea general era:

            - dividir el trabajo en partes pequenas,
            - enviar esas partes a varias maquinas,
            - procesarlas en paralelo,
            - y luego combinar los resultados.

            Por eso se habla de dos fases principales:

            - **Map**: transformar datos o emitir pares clave-valor
            - **Reduce**: agrupar y combinar resultados

            ### Ejemplo simple

            Si quieres contar palabras en millones de documentos:

            - en la fase **Map**, cada nodo cuenta palabras en su fragmento,
            - en la fase **Reduce**, se combinan los conteos para obtener el total global.

            ### Idea clave

            - **MapReduce si procesa datos**
            - pero lo hace con un modelo mas rigido y mas pesado que lo que vino despues

            ---

            ## 3. Que limitacion tenia MapReduce?

            MapReduce fue muy importante historicamente, pero tenia una limitacion fuerte:

            > dependia mucho de escribir y leer datos intermedios en disco entre etapas.

            Eso significa que si un trabajo tenia varios pasos, el flujo tipico se parecia a esto:

            1. leer datos,
            2. procesar,
            3. escribir resultado intermedio a disco,
            4. volver a leer,
            5. volver a procesar,
            6. volver a escribir.

            Esto funcionaba, pero era costoso.

            Se volvia especialmente pesado en:

            - algoritmos iterativos,
            - machine learning,
            - pipelines largos de transformacion,
            - analisis interactivo,
            - procesos donde el mismo dataset se reutiliza varias veces.

            ### Idea clave

            MapReduce resolvia el problema de procesar datos grandes, pero podia volverse **lento y pesado**
            cuando el trabajo tenia muchos pasos o mucha iteracion.

            ---

            ## 4. Ahi aparece Spark

            **Spark** aparece como una evolucion importante de ese modelo.

            No porque Hadoop fuera "malo", sino porque empezaron a ser mas comunes problemas que pedian:

            - mas velocidad,
            - mas flexibilidad,
            - menos dependencia del disco,
            - APIs mas comodas,
            - mas facilidad para construir pipelines complejos.

            Spark mantiene la idea de fondo:

            - datos grandes,
            - multiples maquinas,
            - procesamiento distribuido,

            pero cambia mucho la forma de ejecutar.

            ### Como mejora Spark a MapReduce?

            La mejora no es solo que Spark sea "mas nuevo". La diferencia importante esta en **como ejecuta los trabajos**,
            **como maneja los datos intermedios** y **que tan flexible es para construir pipelines**.

            - **Menos dependencia del disco**: Spark intenta mantener mucho mas trabajo en memoria.
            - **Mejor para trabajos iterativos**: penaliza menos repetir operaciones sobre los mismos datos.
            - **Pipelines mas flexibles**: no obliga a pensar todo como `Map` y `Reduce`.
            - **Un solo motor para varios estilos de trabajo**: batch, SQL, ML y streaming.
            - **Mejor experiencia de desarrollo**: DataFrames y SQL son mucho mas expresivos.
            - **Mejor observabilidad**: la Spark UI permite entender mejor que esta pasando.

            ### Idea clave

            - **MapReduce** = modelo clasico, robusto, pero mas rigido y costoso
            - **Spark** = motor mas moderno, flexible y eficiente para muchos casos

            ---

            ## 5. YARN: quien organiza los recursos

            Aqui suele aparecer una confusion muy comun:

            - **YARN no es Spark**
            - **YARN no es HDFS**
            - **YARN no procesa datos directamente**

            **YARN** sirve para **administrar recursos del cluster**.
            Su trabajo es decidir cosas como:

            - que aplicacion corre,
            - en que maquinas corre,
            - cuanta memoria recibe,
            - cuantos CPU recibe,
            - como conviven varios trabajos al mismo tiempo.

            En otras palabras:

            - **HDFS** guarda los datos
            - **MapReduce o Spark** procesan los datos
            - **YARN** organiza los recursos para que eso ocurra

            > **YARN = administrador de recursos**

            ---

            ## 6. Como pensar esto en Databricks

            Aunque en Databricks no montes Hadoop manualmente, la logica conceptual sigue siendo la misma.
            En Big Data siempre aparecen tres problemas distintos:

            1. **Donde viven los datos**
            2. **Quien los procesa**
            3. **Quien administra los recursos**

            En el ecosistema clasico eso se veia asi:

            - **HDFS**: almacenamiento
            - **MapReduce / Spark**: procesamiento
            - **YARN**: administracion de recursos

            En plataformas modernas como Databricks, muchas de esas piezas estan mas integradas o abstraidas,
            pero el problema de fondo sigue siendo el mismo.

            ### Que idea debes llevarte

            - **Hadoop** te da el contexto del problema Big Data.
            - **YARN** te muestra que ejecutar trabajos distribuidos requiere coordinar recursos.
            - **Spark** es el motor moderno que nos interesa aprender a usar.
            - **Databricks** es la plataforma que nos permite practicarlo con menos dolor.
            """
        ),
        section_header("3", "Preparacion del entorno y dataset"),
        md(
            """
            Usaremos el dataset publico de **NYC Yellow Taxi 2023-01**, suficientemente grande para mostrar
            diferencias de API y ejecucion sin ser inabordable para Community Edition.
            """
        ),
        code(
            """
            # Rutas estandar del laboratorio
            DBFS_DATA_DIR = "/FileStore/datasets/taxi"
            DBFS_DATA_FILE = f"{DBFS_DATA_DIR}/yellow_taxi_2023_01.parquet"
            LOCAL_DATA_FILE = f"/dbfs{DBFS_DATA_FILE}"

            dbutils.fs.mkdirs(DBFS_DATA_DIR)
            print(DBFS_DATA_FILE)
            """
        ),
        code(
            """
            %sh
            set -e
            if [ ! -f /dbfs/FileStore/datasets/taxi/yellow_taxi_2023_01.parquet ]; then
              wget -q "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet" \
                   -O /tmp/yellow_taxi_2023_01.parquet
              cp /tmp/yellow_taxi_2023_01.parquet /dbfs/FileStore/datasets/taxi/
            fi
            echo "Archivo listo:"
            du -sh /dbfs/FileStore/datasets/taxi/yellow_taxi_2023_01.parquet
            """
        ),
        code(
            """
            # Carga inicial con Spark
            from pyspark.sql import functions as F

            sdf = spark.read.parquet(DBFS_DATA_FILE)
            print(f"Particiones iniciales: {sdf.rdd.getNumPartitions()}")
            print(f"Columnas: {len(sdf.columns)}")
            sdf.printSchema()
            """
        ),
        code(
            """
            # Primera action: dispara un job real
            total_rows = sdf.count()
            print(f"Filas: {total_rows:,}")
            print("\\nAhora abre Spark UI -> Jobs y observa:")
            print("- cuantas stages se ejecutaron")
            print("- cuantos tasks hubo")
            print("- cuanto tardo la lectura")
            """
        ),
        section_header("4", "Modelo mental de Spark"),
        md(
            """
            ## Transformations vs Actions

            Spark construye un **plan lazy**. Mientras encadenas `select`, `filter`, `withColumn` o `groupBy`,
            generalmente no procesa datos todavia. El trabajo real ocurre cuando llamas una **action**:

            - `count()`
            - `show()`
            - `collect()`
            - `write...save(...)`

            Esta separacion es clave para entender por que una celda inocente a veces tarda segundos o minutos.
            """
        ),
        code(
            """
            base = (
                sdf
                .filter(F.col("fare_amount") > 0)
                .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
                .withColumn("tip_pct", F.col("tip_amount") / F.col("fare_amount") * 100)
            )

            print("Hasta aqui no deberia haberse ejecutado un job pesado: solo construimos el plan.")
            print(base)
            """
        ),
        code(
            """
            # Narrow + Wide transformations
            hourly = (
                base
                .groupBy("pickup_hour")
                .agg(
                    F.count("*").alias("viajes"),
                    F.avg("fare_amount").alias("tarifa_promedio"),
                    F.avg("tip_pct").alias("tip_pct_promedio"),
                )
                .orderBy("pickup_hour")
            )

            hourly.show(24, truncate=False)
            print("\\nObserva en Spark UI que groupBy y orderBy suelen introducir shuffles.")
            """
        ),
        code(
            """
            print("Plan fisico simplificado:")
            hourly.explain()
            """
        ),
        md(
            """
            ## Senales de que un paso puede ser caro

            Cuando trabajamos con Spark, una transformacion puede verse simple en el codigo, pero ser costosa
            en la ejecucion real. Por eso no basta con leer el notebook: tambien hay que revisar el
            **plan de ejecucion** con `explain()` y la **Spark UI**.

            Estas son algunas senales importantes:

            ### `Exchange` en `explain()`

            Si en el plan aparece `Exchange`, normalmente significa que Spark necesita
            **redistribuir datos entre particiones**.

            Eso suele ocurrir en operaciones como:

            - `groupBy`
            - `join`
            - `distinct`
            - `orderBy`

            Este movimiento de datos entre nodos o entre particiones se conoce como **shuffle**, y suele ser
            una de las partes mas costosas de Spark porque implica:

            - mover datos por red,
            - escribir y leer datos intermedios,
            - esperar a que varias tareas terminen antes de continuar.

            > Regla practica: si aparece `Exchange`, preguntate si estas provocando un shuffle y si realmente es necesario.

            ### `SortMergeJoin`

            Cuando Spark usa `SortMergeJoin`, normalmente esta resolviendo un `join` entre tablas grandes o medianas.
            Este tipo de join puede ser costoso porque requiere:

            - redistribuir datos por clave,
            - ordenar datos en ambos lados,
            - coordinar mas trabajo entre particiones.

            No siempre es malo: muchas veces es la estrategia correcta.
            Pero si una de las tablas es pequena, puede ser mejor un **`BroadcastHashJoin`**, porque Spark envia
            esa tabla pequena a cada executor y evita gran parte del shuffle.

            > Idea clave: si una tabla es de referencia y cabe razonablemente en memoria, un broadcast join suele ser mucho mas eficiente.

            ### `BroadcastHashJoin`

            Este join suele ser una buena senal cuando una de las tablas es pequena.
            Spark replica esa tabla pequena en los executors y hace el cruce localmente, en vez de redistribuir ambas tablas.

            Ventajas:

            - menos trafico por red,
            - menos shuffle,
            - menos costo de ordenamiento,
            - mejor tiempo de respuesta en muchos casos.

            Aun asi, no todo deberia hacerse con broadcast. Si la tabla "pequena" en realidad no lo es tanto,
            puedes generar presion de memoria.

            ### `PythonUDF` en el plan

            Si aparece `PythonUDF`, es una senal de alerta.
            Eso significa que parte de la logica sale del motor optimizado de Spark y pasa por Python, lo cual
            introduce costos de:

            - serializacion,
            - deserializacion,
            - cruce entre JVM y Python,
            - menor capacidad de optimizacion por parte de Spark.

            En muchos casos, una `PythonUDF` sera mas lenta que una expresion nativa con funciones de
            `pyspark.sql.functions`.

            Por eso, antes de usar una UDF, conviene preguntarse:

            - esto se puede expresar con `F.when`, `F.col`, `F.regexp_extract`, `F.concat`, `F.date_format`, etc.?
            - puedo evitar logica fila por fila en Python?
            - una `pandas_udf` seria mejor que una UDF tradicional?

            > Regla de oro: primero intenta resolver el problema con funciones nativas de Spark; usa UDFs solo cuando realmente no haya una alternativa razonable.

            ### Otras pistas utiles

            Ademas de las tres senales anteriores, conviene estar atento a estos sintomas:

            - **Muchos stages** para una operacion que parecia sencilla.
            - **Tasks muy desbalanceadas**: algunas terminan rapido y una o dos tardan muchisimo.
            - **Spill a disco**: senal de que falto memoria para procesar en RAM.
            - **`collect()` o `toPandas()`** en un punto temprano del pipeline.
            - **`repartition(1)`** sin una razon fuerte.
            - **`orderBy` global** sobre datasets grandes, especialmente si no era estrictamente necesario.

            ### Que hacer cuando detectas estas senales

            Si ves alguna de estas banderas, no significa automaticamente que el codigo este mal, pero si que vale la pena revisar:

            1. si hay un shuffle evitable,
            2. si puedes reducir columnas antes del join o del groupBy,
            3. si puedes filtrar antes de una operacion costosa,
            4. si conviene usar `broadcast`,
            5. si una UDF puede reemplazarse por funciones nativas,
            6. si el numero de particiones tiene sentido para el tamano de los datos y del cluster.

            ### Resumen

            Una transformacion en Spark puede ser costosa aunque el codigo parezca corto.
            Las senales mas comunes son:

            - `Exchange`: probablemente hay shuffle.
            - `SortMergeJoin`: join potencialmente caro.
            - `BroadcastHashJoin`: suele ser mejor para tablas pequenas.
            - `PythonUDF`: alerta de sobrecosto por salir del motor nativo.
            - spills, skew, `collect()` temprano o `repartition(1)`: sintomas clasicos de problemas de diseno.

            Aprender a reconocer estas senales es parte fundamental de usar Spark correctamente.
            """
        ),
        section_header("5", "Que puede salir mal"),
        md(
            """
            ## Anti-patrones y problemas tipicos

            Aprender Spark sin hablar de fallos reales deja una vision incompleta. Estos son errores comunes:

            1. **`collect()` o `toPandas()` demasiado pronto**: traes todo al driver y pierdes la ventaja distribuida.
            2. **`repartition(1)` por comodidad**: fuerzas a un solo task y conviertes el pipeline en cuello de botella.
            3. **Python UDFs innecesarias**: cada fila cruza Python/JVM y el trabajo se vuelve mucho mas lento.
            4. **Shuffles invisibles**: `groupBy`, `join`, `distinct`, `orderBy` suelen disparar redistribucion de datos.
            5. **Skew**: una clave concentra demasiadas filas y un task queda haciendo casi todo el trabajo.
            6. **Cache sin criterio**: llenar memoria con DataFrames que usas una sola vez.
            7. **Comparaciones injustas**: medir Spark contra Pandas sin contar tiempo de lectura, sin mismas operaciones o sin materializar resultados.
            """
        ),
        code(
            """
            print("Checklist mental antes de ejecutar un pipeline Spark:")
            print("1. Donde ocurre la ACTION que dispara el job?")
            print("2. Hay joins, groupBy u orderBy que provoquen shuffle?")
            print("3. Estoy moviendo datos al driver sin necesidad?")
            print("4. Estoy usando funciones nativas o Python UDFs?")
            print("5. El numero de particiones tiene sentido para este cluster?")
            """
        ),
        md(
            """
            ## Que mirar en la Spark UI

            Cuando una celda corra mas lento de lo esperado, revisa:

            - **Jobs**: cuantos jobs disparaste realmente.
            - **Stages**: donde empieza el shuffle.
            - **Tasks**: si hay una particion mucho mas lenta que las otras.
            - **SQL/DataFrame tab**: plan fisico, exchange, broadcast, sort merge join.
            - **Storage tab**: que se cacheo en memoria y con que tamano.
            """
        ),
        section_header("6", "Spark SQL como puente para analitica"),
        md(
            """
            Una de las razones por las que Spark se vuelve tan util en organizaciones reales es que no obliga
            a todo el mundo a pensar solo en Python. Con **Spark SQL**, analistas e ingenieros pueden trabajar
            sobre el mismo motor con lenguajes distintos.
            """
        ),
        code(
            """
            # Registrar una vista temporal para consultar con SQL
            base.createOrReplaceTempView("taxi_base")

            spark.sql(
                '''
                SELECT
                  pickup_hour,
                  COUNT(*) AS viajes,
                  ROUND(AVG(fare_amount), 2) AS tarifa_promedio
                FROM taxi_base
                GROUP BY pickup_hour
                ORDER BY pickup_hour
                '''
            ).show(10)
            """
        ),
        md(
            """
            ## Por que esta seccion importa

            - Si vienes de analitica tradicional, SQL te da una entrada muy natural.
            - Si vienes de Python, entiendes que Spark no es solo una libreria sino tambien un motor SQL.
            - En equipos mixtos, esta dualidad vuelve a Spark muy atractivo frente a alternativas mas locales.
            """
        ),
        section_header("7", "Pandas vs Dask vs PySpark"),
        code(
            """
            import time
            import pandas as pd
            import dask.dataframe as dd

            t0 = time.time()
            pdf = pd.read_parquet(LOCAL_DATA_FILE)
            t_pandas_load = time.time() - t0

            t0 = time.time()
            ddf = dd.read_parquet(LOCAL_DATA_FILE)
            t_dask_plan = time.time() - t0

            t0 = time.time()
            sdf2 = spark.read.parquet(DBFS_DATA_FILE)
            t_spark_plan = time.time() - t0

            print("=== Carga / plan inicial ===")
            print(f"Pandas  : {t_pandas_load:.2f}s  | filas={len(pdf):,}")
            print(f"Dask    : {t_dask_plan:.4f}s | npartitions={ddf.npartitions} (lazy)")
            print(f"PySpark : {t_spark_plan:.4f}s | partitions={sdf2.rdd.getNumPartitions()} (lazy)")
            """
        ),
        md(
            """
            ### Como leer esta comparacion

            - Si Dask o Spark "cargan" en milisegundos, no es magia: normalmente **solo construyeron el plan**.
            - Si Pandas tarda mas al inicio, es porque **ya materializo** los datos en memoria.
            - Una comparacion justa debe medir acciones equivalentes.
            """
        ),
        code(
            """
            print("=== Filtrado equivalente ===")

            t0 = time.time()
            pdf_f = pdf[(pdf["fare_amount"] > 10) & (pdf["trip_distance"] > 1)]
            pandas_time = time.time() - t0

            t0 = time.time()
            ddf_f = ddf[(ddf["fare_amount"] > 10) & (ddf["trip_distance"] > 1)]
            dask_count = len(ddf_f)
            dask_time = time.time() - t0

            t0 = time.time()
            sdf_f = sdf2.filter((F.col("fare_amount") > 10) & (F.col("trip_distance") > 1))
            spark_count = sdf_f.count()
            spark_time = time.time() - t0

            print(f"Pandas  -> {len(pdf_f):,} filas | {pandas_time:.3f}s")
            print(f"Dask    -> {dask_count:,} filas | {dask_time:.3f}s")
            print(f"PySpark -> {spark_count:,} filas | {spark_time:.3f}s")
            print(f"Coinciden: {len(pdf_f) == dask_count == spark_count}")
            """
        ),
        code(
            """
            print("=== GroupBy equivalente ===")

            t0 = time.time()
            pdf_h = (
                pdf.assign(pickup_hour=pd.to_datetime(pdf["tpep_pickup_datetime"]).dt.hour)
                   .groupby("pickup_hour")
                   .agg(viajes=("fare_amount", "count"),
                        tarifa_prom=("fare_amount", "mean"))
                   .sort_index()
            )
            pandas_group_time = time.time() - t0

            t0 = time.time()
            ddf_h = (
                ddf.assign(pickup_hour=dd.to_datetime(ddf["tpep_pickup_datetime"]).dt.hour)
                   .groupby("pickup_hour")
                   .agg({"fare_amount": ["count", "mean"]})
                   .compute()
                   .sort_index()
            )
            ddf_h.columns = ["viajes", "tarifa_prom"]
            dask_group_time = time.time() - t0

            t0 = time.time()
            sdf_h = (
                sdf2.withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
                    .groupBy("pickup_hour")
                    .agg(
                        F.count("*").alias("viajes"),
                        F.avg("fare_amount").alias("tarifa_prom"),
                    )
                    .orderBy("pickup_hour")
            )
            sdf_h.show(5)
            spark_group_time = time.time() - t0

            print(f"Pandas  groupBy: {pandas_group_time:.3f}s")
            print(f"Dask    groupBy: {dask_group_time:.3f}s")
            print(f"PySpark groupBy: {spark_group_time:.3f}s")
            """
        ),
        md(
            """
            ## Por que usar Spark en vez de Dask o Pandas

            Elegir Spark no significa que Pandas o Dask sean "malas" herramientas.
            En realidad, las tres resuelven problemas distintos y tienen fortalezas diferentes. La ventaja
            de Spark aparece con mas claridad cuando el problema deja de ser solo "hacer analisis" y pasa
            a ser tambien **escalar, operar, monitorear y mantener pipelines de datos de forma confiable**.

            ### Spark no gana solo por velocidad

            Muchas veces se piensa que Spark se usa unicamente porque "es mas rapido".
            Eso es una simplificacion. En datasets pequenos o medianos, **Pandas puede ser incluso mas conveniente**
            por su simplicidad, y en escenarios intermedios **Dask puede ofrecer una transicion muy comoda**
            desde la API de Pandas.

            La ventaja real de Spark esta en que combina:

            - procesamiento distribuido,
            - optimizacion automatica,
            - herramientas maduras de observabilidad,
            - un ecosistema robusto para produccion,
            - y una forma mas estandarizada de construir pipelines analiticos a gran escala.

            ### 1. `Catalyst optimizer`: Spark no solo ejecuta, tambien optimiza

            Una de las mayores fortalezas de Spark es su optimizador interno, llamado **Catalyst**.
            Cuando escribes una transformacion en DataFrames o Spark SQL, Spark no ejecuta literalmente el codigo
            tal como lo escribiste: primero construye un plan logico y luego intenta **reescribirlo y optimizarlo**.

            Eso le permite, entre otras cosas:

            - empujar filtros lo mas temprano posible,
            - eliminar columnas innecesarias,
            - reorganizar partes del plan,
            - elegir estrategias de join,
            - reducir trabajo redundante.

            En otras palabras, Spark no es solamente una libreria de transformacion de datos; tambien es un
            **motor de ejecucion con capacidad de optimizacion**.

            > En Pandas, en cambio, casi toda la responsabilidad de escribir una secuencia eficiente recae mucho mas directamente en quien programa.

            ### 2. `Spark SQL`: un puente muy fuerte entre ingenieria y analitica

            Otra gran ventaja es **Spark SQL**.
            Spark no solo ofrece una API en Python o Scala, sino tambien un motor SQL muy potente. Esto tiene
            varias implicaciones pedagogicas y profesionales:

            - Personas con perfil analitico pueden trabajar en SQL sin dominar toda la API de PySpark.
            - Equipos mixtos pueden colaborar mejor.
            - Muchas transformaciones complejas se expresan de forma mas clara en SQL.
            - Es mas facil conectar notebooks exploratorios con pipelines mas formales.

            Esto hace que Spark sea especialmente util en organizaciones donde conviven:

            - ingenieros de datos,
            - analistas,
            - cientificos de datos,
            - equipos de BI.

            ### 3. UI madura: observar la ejecucion es parte del aprendizaje

            Una diferencia muy importante frente a Pandas, y tambien frente a muchos usos sencillos de Dask, es que
            Spark ofrece una **interfaz madura de observabilidad**.

            Con la **Spark UI** puedes ver:

            - cuantos jobs se ejecutaron,
            - cuantos stages produjo una celda,
            - cuantos tasks corrieron,
            - donde hubo shuffle,
            - cuanto tiempo tomo cada parte,
            - si hubo skew,
            - si se derramo memoria a disco,
            - que estrategia de join uso el motor.

            Esto no es solo una ventaja tecnica: tambien es una ventaja pedagogica.
            Permite enseÃ±ar que en sistemas distribuidos no basta con obtener el resultado correcto; tambien importa **como** se calculo ese resultado.

            ### 4. Ecosistema operacional: Spark suele encajar mejor en produccion

            Cuando un proyecto crece, el problema ya no es solo transformar datos, sino tambien operar procesos de
            forma repetible y segura.

            Ahi Spark suele ofrecer una ventaja clara porque encaja muy bien con un ecosistema de produccion que incluye:

            - jobs programados,
            - tablas gestionadas,
            - integracion con catalogos y gobernanza,
            - formatos modernos como Delta Lake,
            - procesamiento batch y streaming,
            - herramientas administradas como Databricks.

            Esto hace que Spark sea frecuente en contextos empresariales donde importa:

            - trazabilidad,
            - reproducibilidad,
            - control de cambios,
            - monitoreo,
            - escalabilidad futura.

            Dask puede ser muy util y elegante para ciertos flujos, pero Spark suele ofrecer una ruta mas estandar
            cuando el objetivo es construir **plataformas de datos** y no solo scripts de analisis.

            ### 5. Joins distribuidos mas robustos

            Los `join` son una de las operaciones mas criticas en datos a escala.
            Cuando las tablas crecen, resolver joins de manera eficiente deja de ser trivial.

            Spark ofrece varias estrategias maduras para esto, por ejemplo:

            - `BroadcastHashJoin` cuando una tabla es pequena,
            - `SortMergeJoin` para tablas grandes,
            - optimizaciones automaticas segun estadisticas y plan.

            Ademas, Spark permite inspeccionar el plan y ver que estrategia eligio. Eso es muy util para diagnosticar
            rendimiento y para enseÃ±ar por que un join a veces explota en costo.

            En Pandas, un join puede ser muy comodo, pero todo ocurre en la memoria local del proceso.
            En Dask, los joins tambien existen, pero cuando la complejidad operacional crece, Spark suele dar mas
            herramientas para entender y controlar el comportamiento.

            ### 6. Spark fuerza un modelo mental util para Big Data

            Pandas invita a pensar en un DataFrame local.
            Eso es una gran ventaja para empezar, pero a escala puede ocultar ciertos costos.

            Spark, en cambio, obliga mas temprano a pensar en preguntas como:

            - cuando se ejecuta realmente el calculo?
            - que operaciones causan shuffle?
            - cuantas particiones hay?
            - estoy moviendo datos al driver?
            - puedo evitar una UDF?
            - este `orderBy` realmente hace falta?

            Ese cambio de mentalidad es muy valioso en cursos de Big Data, porque acerca al estudiante a la logica real
            de los sistemas distribuidos.

            ### 7. Delta Lake amplia el valor de Spark

            En entornos como Databricks, Spark no aparece solo: suele venir acompaÃ±ado de **Delta Lake**, que agrega
            capacidades como:

            - transacciones ACID,
            - historial de versiones,
            - `MERGE` / upsert,
            - rollback y restore,
            - mayor confiabilidad para tablas analiticas.

            Eso significa que Spark no solo ayuda a **procesar** datos, sino tambien a **gestionarlos mejor**
            una vez que el pipeline entra en produccion.

            ### Entonces, cuando elegir cada uno?

            ### Usa Pandas cuando:

            - los datos caben comodamente en memoria,
            - necesitas explorar rapido,
            - quieres la menor friccion posible,
            - el objetivo es analisis local o prototipado.

            ### Usa Dask cuando:

            - quieres una API parecida a Pandas,
            - los datos ya no caben tan bien en RAM,
            - necesitas escalar un poco sin cambiar demasiado tu forma de trabajar,
            - el problema sigue siendo mas analitico que operacional.

            ### Usa Spark cuando:

            - el volumen de datos crece de forma seria,
            - necesitas joins, agregaciones o ETLs distribuidos con observabilidad,
            - quieres una ruta mas estandar hacia produccion,
            - el equipo combina SQL, notebooks y pipelines,
            - necesitas tablas confiables, historial y gobierno del dato.

            ### Resumen

            Spark no siempre es la mejor herramienta para todo, pero si suele ser la mas solida cuando el problema combina:

            - **escala**,
            - **distribucion**,
            - **operacion en produccion**,
            - **observabilidad**,
            - y **mantenimiento a largo plazo**.

            Dask es muy valioso cuando quieres una transicion suave desde Pandas.
            Pandas sigue siendo excelente para analisis local y exploracion rapida.
            Pero cuando el objetivo ya no es solo analizar datos, sino construir pipelines robustos y sostenibles,
            **Spark suele ofrecer un camino mas estandarizado y mas maduro**.
            """
        ),
        code(
            """
            print("=== Join pequeno de referencia ===")

            zone_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv"
            zones_pdf = pd.read_csv(zone_url)[["LocationID", "Borough", "Zone"]].rename(
                columns={
                    "LocationID": "PULocationID",
                    "Borough": "pickup_borough",
                    "Zone": "pickup_zone",
                }
            )

            zones_sdf = spark.createDataFrame(zones_pdf)

            t0 = time.time()
            joined = sdf2.join(F.broadcast(zones_sdf), on="PULocationID", how="left")
            joined.select("PULocationID", "pickup_borough", "pickup_zone").show(5, truncate=False)
            join_time = time.time() - t0

            print(f"Join Spark con broadcast: {join_time:.3f}s")
            print("Busca en el plan/SQL tab si aparece BroadcastHashJoin.")
            """
        ),
        code(
            """
            print("=== Anti-patron: Python UDF vs funcion nativa ===")
            from pyspark.sql.functions import udf
            from pyspark.sql.types import StringType

            sample = sdf2.select("tpep_pickup_datetime", "tpep_dropoff_datetime").limit(500000)
            sample = sample.withColumn(
                "duracion_min",
                (F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")) / 60
            )

            @udf(StringType())
            def clasificar_udf(minutos):
                if minutos is None:
                    return None
                if minutos < 5:
                    return "corto"
                if minutos < 20:
                    return "medio"
                return "largo"

            t0 = time.time()
            udf_result = sample.withColumn("tipo", clasificar_udf(F.col("duracion_min")))
            udf_result.groupBy("tipo").count().show()
            udf_time = time.time() - t0

            t0 = time.time()
            native_result = sample.withColumn(
                "tipo",
                F.when(F.col("duracion_min") < 5, "corto")
                 .when(F.col("duracion_min") < 20, "medio")
                 .otherwise("largo")
            )
            native_result.groupBy("tipo").count().show()
            native_time = time.time() - t0

            print(f"Python UDF : {udf_time:.2f}s")
            print(f"Nativo Spark: {native_time:.2f}s")
            if native_time > 0:
                print(f"Speedup nativo: {udf_time / native_time:.1f}x")
            """
        ),
        code(
            """
            print("=== Anti-patron: traer demasiado al driver ===")
            driver_preview = sdf2.select("VendorID", "fare_amount", "trip_distance").limit(5).toPandas()
            print(driver_preview)
            print("\\nEsto es seguro porque usamos limit(5).")
            print("Lo peligroso seria hacer toPandas() sobre millones de filas.")
            """
        ),
        md(
            """
            ## Cuando Pandas o Dask siguen siendo la mejor opcion

            - Si el dataset cabe en memoria y la prioridad es velocidad de desarrollo, Pandas suele ganar.
            - Si tu equipo ya piensa en Pandas y necesitas escalar un poco sin reescribir toda la API, Dask puede ser ideal.
            - Si necesitas observabilidad, SQL distribuido y estandar operacional, Spark gana terreno rapidamente.
            """
        ),
        section_header("8", "Delta Lake en la practica"),
        md(
            """
            Delta Lake resuelve un dolor real: un lago de datos con archivos Parquet sueltos no ofrece,
            por si mismo, transacciones, historial, rollback ni upserts consistentes.
            """
        ),
        code(
            """
            DELTA_PATH = "/FileStore/delta/taxi_sesion8"

            sdf_delta = (
                sdf2
                .filter(F.col("fare_amount") > 0)
                .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
                .withColumn(
                    "tipo_viaje",
                    F.when(F.col("trip_distance") < 2, "corto")
                     .when(F.col("trip_distance") < 8, "medio")
                     .otherwise("largo")
                )
            )

            (sdf_delta.write
                .format("delta")
                .mode("overwrite")
                .option("overwriteSchema", "true")
                .save(DELTA_PATH))

            print(DELTA_PATH)
            """
        ),
        code(
            """
            from delta.tables import DeltaTable
            import json

            delta_table = DeltaTable.forPath(spark, DELTA_PATH)
            delta_table.history(5).select("version", "timestamp", "operation").show(truncate=False)

            print("Primeras lineas del transaction log:")
            log_head = dbutils.fs.head(DELTA_PATH + "/_delta_log/00000000000000000000.json", 1000)
            for line in log_head.split("\\n")[:3]:
                if line.strip():
                    print(json.dumps(json.loads(line), indent=2)[:300])
            """
        ),
        code(
            """
            print("=== Simular datos malos y recuperar ===")

            bad_rows = spark.createDataFrame([
                (1, -999.0, "corrupto"),
                (2, -888.0, "corrupto"),
            ], ["VendorID", "fare_amount", "origen"])

            DEMO_DELTA_PATH = "/FileStore/delta/taxi_sesion8_demo"
            spark.createDataFrame([(1, 10.0, "ok")], ["VendorID", "fare_amount", "origen"]) \\
                 .write.format("delta").mode("overwrite").save(DEMO_DELTA_PATH)

            demo = DeltaTable.forPath(spark, DEMO_DELTA_PATH)
            bad_rows.write.format("delta").mode("append").save(DEMO_DELTA_PATH)

            print("Tabla con filas corruptas:")
            spark.read.format("delta").load(DEMO_DELTA_PATH).show()

            print("Restaurando version 0...")
            demo.restoreToVersion(0)
            spark.read.format("delta").load(DEMO_DELTA_PATH).show()
            """
        ),
        md(
            """
            ### Beneficio real de Delta

            - **Time Travel**: puedes leer una version anterior.
            - **Restore**: puedes volver atras rapidamente tras datos corruptos.
            - **Merge**: puedes hacer upsert sin reescribir manualmente todo.
            - **Transaction log**: sabes que cambios ocurrieron y cuando.
            """
        ),
        section_header("9", "Taller guiado"),
        md(
            """
            Estas preguntas estan disenadas para que el estudiante **no pueda aprobar por accidente**.
            Si no completas la solucion, la celda debe fallar explicitamente.
            """
        ),
        code(
            """
            # Pregunta 1
            # Top 3 horas del dia con mayor score = numero de viajes * tarifa promedio

            raise NotImplementedError(
                "Completa esta celda: filtra outliers, agrupa por hora, calcula score y muestra el top 3."
            )
            """
        ),
        code(
            """
            # Pregunta 2
            # Borough con mejor ratio de propina, considerando solo grupos con mas de 1000 viajes

            raise NotImplementedError(
                "Completa esta celda usando el DataFrame joined y calcula tip_ratio_pct correctamente."
            )
            """
        ),
        code(
            """
            # Pregunta 3
            # Benchmark Dask vs PySpark para percentil 90 por dia de semana

            raise NotImplementedError(
                "Implementa ambos calculos y compara tiempos usando acciones equivalentes."
            )
            """
        ),
        md(
            """
            ## Sugerencia didactica

            Para la clase, puedes duplicar estas tres celdas en una version de profesor con solucion,
            o publicar las soluciones en un notebook aparte para retroalimentacion posterior.
            """
        ),
        section_header("10", "Checklist final de produccion"),
        md(
            """
            Antes de mover un notebook de demo a pipeline real, preguntate:

            - Los datos seguiran cabiendo en el cluster cuando crezcan 10x?
            - Hay `collect()`, `toPandas()` o `repartition(1)` escondidos?
            - Los joins pequenos usan `broadcast` cuando aplica?
            - Las UDFs Python son realmente inevitables?
            - La tabla final necesita versionado, upserts o rollback? Si si, Delta ayuda mucho.
            - Ya revisaste la Spark UI y el `explain()` del paso critico?

            Si puedes responder estas preguntas con evidencia, ya no estas "corriendo Spark":
            estas **razonando sobre sistemas distribuidos**.
            """
        ),
    ]

    return cells


if __name__ == "__main__":
    cells = build_cells()
    validate(cells)
    save(cells, "Cuadernos/7_Hadoop_YARN_Spark_Databricks.ipynb")

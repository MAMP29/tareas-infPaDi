
import os
import re
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuración de estilo para gráficos
plt.style.use('ggplot')
sns.set_palette("colorblind")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 11
plt.rcParams['ytick.labelsize'] = 11

class OpenMPAnalyzer:
    def __init__(self, data_dir="/tmp"):
        """
        Inicializa el analizador con el directorio donde se encuentran los archivos de datos.
        
        Args:
            data_dir: Directorio donde se encuentran los archivos de tiempo
        """
        self.data_dir = data_dir
        self.hilos_data = {}  # Datos de tiempos por hilos
        self.limite_data = {}  # Datos de tiempos con límites
        self.df_hilos = None  # DataFrame consolidado para datos de hilos
        self.df_limite = None  # DataFrame consolidado para datos de límite
        
    def cargar_datos(self):
        """Carga todos los archivos de datos relevantes y los organiza en estructuras de datos"""
        print("Cargando archivos de datos...")
        
        # Cargar archivos de tiempos por hilos
        archivos_hilos = glob.glob(os.path.join(self.data_dir, "tiempos*.txt"))
        for archivo in archivos_hilos:
            num_hilos = int(re.search(r'tiempos(\d+)\.txt', archivo).group(1))
            self.hilos_data[num_hilos] = self._procesar_archivo(archivo)
            print(f"  - Cargado {archivo}, {len(self.hilos_data[num_hilos])} registros")
            
        # Cargar archivos de límites
        archivos_limite = glob.glob(os.path.join(self.data_dir, "limite*.txt"))
        for archivo in archivos_limite:
            valor_limite = int(re.search(r'limite(\d+)\.txt', archivo).group(1))
            self.limite_data[valor_limite] = self._procesar_archivo(archivo)
            print(f"  - Cargado {archivo}, {len(self.limite_data[valor_limite])} registros")
        
        # Consolidar datos en DataFrames
        self._consolidar_datos()
        
    def _procesar_archivo(self, ruta_archivo):
        """
        Procesa un archivo de datos y extrae tiempos por modo de ejecución.
        
        Args:
            ruta_archivo: Ruta al archivo de datos
            
        Returns:
            dict: Tiempos organizados por modo y forma de ejecución
        """
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
            
        # Dividir en secciones
        secciones = re.split(r'\n\n', contenido.strip())
        resultados = {}
        
        for seccion in secciones:
            lineas = seccion.strip().split('\n')
            if not lineas:
                continue
                
            titulo = lineas[0]
            tiempos = [float(t) for t in lineas[1:] if t.strip()]
            
            # Detectar el tipo de modo por el título
            if "Forma 1:" in titulo:
                modo = "Forma 1 (OMP_NUM_THREADS)"
            elif "Forma 2:" in titulo:
                modo = "Forma 2 (omp_set_num_threads)"
            elif "Forma 3:" in titulo:
                modo = "Forma 3 (num_threads)"
            elif "OMP_THREAD_LIMIT" in titulo and "modo 1" in titulo:
                modo = "Límite-Forma 1"
            elif "OMP_THREAD_LIMIT" in titulo and "modo 2" in titulo:
                modo = "Límite-Forma 2"
            elif "OMP_THREAD_LIMIT" in titulo and "modo 3" in titulo:
                modo = "Límite-Forma 3"
            else:
                modo = titulo  # Por si hay un formato inesperado
                
            resultados[modo] = tiempos
            
        return resultados
    
    def _consolidar_datos(self):
        """Consolida los datos en DataFrames para facilitar el análisis"""
        # DataFrame para datos de hilos
        rows_hilos = []
        for num_hilos, modos in self.hilos_data.items():
            for modo, tiempos in modos.items():
                for tiempo in tiempos:
                    rows_hilos.append({
                        'num_hilos': num_hilos,
                        'modo': modo,
                        'tiempo': tiempo
                    })
        self.df_hilos = pd.DataFrame(rows_hilos)
        
        # DataFrame para datos de límites
        rows_limite = []
        for valor_limite, modos in self.limite_data.items():
            for modo, tiempos in modos.items():
                for tiempo in tiempos:
                    rows_limite.append({
                        'limite': valor_limite,
                        'modo': modo,
                        'tiempo': tiempo
                    })
        self.df_limite = pd.DataFrame(rows_limite)
    
    def calcular_estadisticas(self):
        """
        Calcula estadísticas relevantes para ambos conjuntos de datos.
        
        Returns:
            tuple: (df_stats_hilos, df_stats_limite) con estadísticas calculadas
        """
        print("Calculando estadísticas...")
        
        # Estadísticas por hilos
        stats_hilos = self.df_hilos.groupby(['num_hilos', 'modo'])['tiempo'].agg([
            ('tiempo_promedio', 'mean'),
            ('tiempo_mediana', 'median'),
            ('desviacion_std', 'std'),
            ('tiempo_min', 'min'),
            ('tiempo_max', 'max'),
            ('num_ejecuciones', 'count')
        ]).reset_index()
        
        # Agregar cálculos de aceleración
        # Primero, obtener tiempos base (1 hilo para cada modo)
        tiempo_base = {}
        for modo in stats_hilos['modo'].unique():
            base = stats_hilos[(stats_hilos['num_hilos'] == 1) & (stats_hilos['modo'] == modo)]['tiempo_promedio'].values
            if len(base) > 0:
                tiempo_base[modo] = base[0]
            else:
                tiempo_base[modo] = 1  # Valor por defecto si no hay referencia
                
        # Calcular aceleración
        def calcular_aceleracion(row):
            return tiempo_base.get(row['modo'], 1) / row['tiempo_promedio']
            
        stats_hilos['aceleracion'] = stats_hilos.apply(calcular_aceleracion, axis=1)
        
        # Calcular eficiencia
        stats_hilos['eficiencia'] = stats_hilos['aceleracion'] / stats_hilos['num_hilos']
        
        # Estadísticas por límites
        stats_limite = self.df_limite.groupby(['limite', 'modo'])['tiempo'].agg([
            ('tiempo_promedio', 'mean'),
            ('tiempo_mediana', 'median'),
            ('desviacion_std', 'std'),
            ('tiempo_min', 'min'),
            ('tiempo_max', 'max'),
            ('num_ejecuciones', 'count')
        ]).reset_index()
        
        return stats_hilos, stats_limite
    
    def generar_visualizaciones(self, stats_hilos, stats_limite):
        """
        Genera diversas visualizaciones para analizar los datos.
        
        Args:
            stats_hilos: DataFrame con estadísticas de hilos
            stats_limite: DataFrame con estadísticas de límites
        """
        # Crear directorio para gráficas si no existe
        output_dir = "resultados_analisis"
        os.makedirs(output_dir, exist_ok=True)
        
        print("Generando visualizaciones...")
        
        # 1. Gráfica de tiempos promedio por número de hilos
        plt.figure(figsize=(14, 8))
        for modo in stats_hilos['modo'].unique():
            data = stats_hilos[stats_hilos['modo'] == modo]
            plt.plot(data['num_hilos'], data['tiempo_promedio'], 'o-', linewidth=2, markersize=8, label=modo)
            
        plt.xscale('log', base=2)  # Escala logarítmica en base 2 para mejor visualización
        plt.xlabel('Número de Hilos')
        plt.ylabel('Tiempo Promedio (segundos)')
        plt.title('Tiempo Promedio de Ejecución por Número de Hilos')
        plt.grid(True, which="both", ls="--", alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{output_dir}/tiempos_promedio_por_hilos.png", dpi=300)
        
        # 2. Gráfica de aceleración por número de hilos
        plt.figure(figsize=(14, 8))
        # Línea de aceleración ideal (referencia)
        hilos_unicos = sorted(stats_hilos['num_hilos'].unique())
        plt.plot(hilos_unicos, hilos_unicos, 'k--', label='Aceleración Ideal', alpha=0.5)
        
        for modo in stats_hilos['modo'].unique():
            data = stats_hilos[stats_hilos['modo'] == modo]
            plt.plot(data['num_hilos'], data['aceleracion'], 'o-', linewidth=2, markersize=8, label=modo)
            
        plt.xscale('log', base=2)
        plt.yscale('log', base=2)
        plt.xlabel('Número de Hilos')
        plt.ylabel('Aceleración (T1/Tn)')
        plt.title('Aceleración vs. Número de Hilos')
        plt.grid(True, which="both", ls="--", alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{output_dir}/aceleracion_por_hilos.png", dpi=300)
        
        # 3. Gráfica de eficiencia por número de hilos
        plt.figure(figsize=(14, 8))
        for modo in stats_hilos['modo'].unique():
            data = stats_hilos[stats_hilos['modo'] == modo]
            plt.plot(data['num_hilos'], data['eficiencia'], 'o-', linewidth=2, markersize=8, label=modo)
            
        plt.xscale('log', base=2)
        plt.xlabel('Número de Hilos')
        plt.ylabel('Eficiencia (Aceleración/Num_Hilos)')
        plt.title('Eficiencia vs. Número de Hilos')
        plt.grid(True, which="both", ls="--", alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{output_dir}/eficiencia_por_hilos.png", dpi=300)
        
        # 4. Boxplots para comparar distribución de tiempos por modo y número de hilos
        # Crear varios gráficos para evitar sobrecargar uno solo
        hilos_unicos = sorted(self.df_hilos['num_hilos'].unique())
        chunk_size = 3  # Número de valores de hilos por gráfica
        
        for i in range(0, len(hilos_unicos), chunk_size):
            chunk = hilos_unicos[i:i+chunk_size]
            plt.figure(figsize=(14, 10))
            
            df_subset = self.df_hilos[self.df_hilos['num_hilos'].isin(chunk)]
            sns.boxplot(x='num_hilos', y='tiempo', hue='modo', data=df_subset)
            
            plt.xlabel('Número de Hilos')
            plt.ylabel('Tiempo (segundos)')
            plt.title(f'Distribución de Tiempos por Modo y Número de Hilos ({chunk[0]}-{chunk[-1]})')
            plt.legend(title='Modo')
            plt.grid(True, axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/boxplot_hilos_{chunk[0]}_{chunk[-1]}.png", dpi=300)
        
        # 5. Comparación de ejecuciones con límite
        plt.figure(figsize=(14, 8))
        sns.barplot(x='limite', y='tiempo_promedio', hue='modo', data=stats_limite)
        plt.xlabel('Valor del Límite (OMP_THREAD_LIMIT)')
        plt.ylabel('Tiempo Promedio (segundos)')
        plt.title('Tiempos Promedio por Límite y Modo')
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/tiempos_por_limite.png", dpi=300)
        
        # 6. Comparación de modos de ejecución (todas las formas juntas)
        plt.figure(figsize=(15, 8))
        
        # Crear subsets por modo
        dfs_por_modo = {}
        for modo in stats_hilos['modo'].unique():
            dfs_por_modo[modo] = stats_hilos[stats_hilos['modo'] == modo]
            
        # Graficar tiempos para cada modo
        for modo, df in dfs_por_modo.items():
            plt.plot(df['num_hilos'], df['tiempo_promedio'], 'o-', linewidth=2, markersize=8, label=modo)
            
        plt.xscale('log', base=2)
        plt.xlabel('Número de Hilos')
        plt.ylabel('Tiempo Promedio (segundos)')
        plt.title('Comparación de Modos de Ejecución')
        plt.grid(True, which="both", ls="--", alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{output_dir}/comparacion_modos.png", dpi=300)
        
        # 7. Comparación de variabilidad (desviación estándar)
        plt.figure(figsize=(14, 8))
        for modo in stats_hilos['modo'].unique():
            data = stats_hilos[stats_hilos['modo'] == modo]
            plt.plot(data['num_hilos'], data['desviacion_std'], 'o-', linewidth=2, markersize=8, label=modo)
            
        plt.xscale('log', base=2)
        plt.xlabel('Número de Hilos')
        plt.ylabel('Desviación Estándar (segundos)')
        plt.title('Variabilidad del Tiempo de Ejecución por Número de Hilos')
        plt.grid(True, which="both", ls="--", alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{output_dir}/variabilidad_por_hilos.png", dpi=300)
        
        # 8. Heatmap de tiempos promedio
        plt.figure(figsize=(16, 10))
        heatmap_data = stats_hilos.pivot(index='modo', columns='num_hilos', values='tiempo_promedio')
        sns.heatmap(heatmap_data, annot=True, fmt=".4f", cmap="YlGnBu", linewidths=.5)
        plt.title('Heatmap de Tiempos Promedio por Modo y Número de Hilos')
        plt.ylabel('Modo de Ejecución')
        plt.xlabel('Número de Hilos')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/heatmap_tiempos.png", dpi=300)
        
        print(f"Visualizaciones guardadas en el directorio: {output_dir}")
        
    def generar_informes(self, stats_hilos, stats_limite):
        """
        Genera informes tabulares con las estadísticas calculadas.
        
        Args:
            stats_hilos: DataFrame con estadísticas de hilos
            stats_limite: DataFrame con estadísticas de límites
        """
        output_dir = "resultados_analisis"
        os.makedirs(output_dir, exist_ok=True)
        
        print("Generando informes...")
        
        # 1. Tabla de estadísticas por hilos
        stats_hilos.to_csv(f"{output_dir}/estadisticas_por_hilos.csv", index=False)
        
        # 2. Tabla de estadísticas por límites
        stats_limite.to_csv(f"{output_dir}/estadisticas_por_limites.csv", index=False)
        
        # 3. Informe de mejor rendimiento por número de hilos
        mejor_rendimiento = stats_hilos.loc[stats_hilos.groupby('num_hilos')['tiempo_promedio'].idxmin()]
        mejor_rendimiento.to_csv(f"{output_dir}/mejor_rendimiento_por_hilos.csv", index=False)
        
        # 4. Informe de mejor aceleración
        mejor_aceleracion = stats_hilos.loc[stats_hilos.groupby('num_hilos')['aceleracion'].idxmax()]
        mejor_aceleracion.to_csv(f"{output_dir}/mejor_aceleracion_por_hilos.csv", index=False)
        
        # 5. Reporte de resumen global en formato de texto
        with open(f"{output_dir}/resumen_analisis.txt", 'w') as f:
            f.write("RESUMEN DEL ANÁLISIS DE RENDIMIENTO OPENMP\n")
            f.write("=======================================\n\n")
            
            # Resumen general
            f.write("RESUMEN GENERAL\n")
            f.write("--------------\n")
            f.write(f"Total de configuraciones de hilos analizadas: {len(stats_hilos['num_hilos'].unique())}\n")
            f.write(f"Modos de ejecución evaluados: {', '.join(stats_hilos['modo'].unique())}\n")
            f.write(f"Número total de ejecuciones: {len(self.df_hilos)}\n\n")
            
            # Mejor rendimiento global
            idx_mejor = stats_hilos['tiempo_promedio'].idxmin()
            mejor_global = stats_hilos.iloc[idx_mejor]
            f.write("MEJOR RENDIMIENTO GLOBAL\n")
            f.write("------------------------\n")
            f.write(f"Modo: {mejor_global['modo']}\n")
            f.write(f"Número de hilos: {mejor_global['num_hilos']}\n")
            f.write(f"Tiempo promedio: {mejor_global['tiempo_promedio']:.6f} segundos\n")
            f.write(f"Aceleración: {mejor_global['aceleracion']:.6f}x\n")
            f.write(f"Eficiencia: {mejor_global['eficiencia']:.6f}\n\n")
            
            # Mejor aceleración
            idx_acel = stats_hilos['aceleracion'].idxmax()
            mejor_acel = stats_hilos.iloc[idx_acel]
            f.write("MEJOR ACELERACIÓN\n")
            f.write("-----------------\n")
            f.write(f"Modo: {mejor_acel['modo']}\n")
            f.write(f"Número de hilos: {mejor_acel['num_hilos']}\n")
            f.write(f"Aceleración: {mejor_acel['aceleracion']:.6f}x\n")
            f.write(f"Tiempo promedio: {mejor_acel['tiempo_promedio']:.6f} segundos\n\n")
            
            # Comparativa entre modos
            f.write("COMPARATIVA ENTRE MODOS (Con 8 hilos)\n")
            f.write("------------------------------------\n")
            hilos_comp = 8  # Comparamos con 8 hilos por ser un valor intermedio común
            comp_8 = stats_hilos[stats_hilos['num_hilos'] == hilos_comp].sort_values('tiempo_promedio')
            for _, row in comp_8.iterrows():
                f.write(f"Modo: {row['modo']}, Tiempo: {row['tiempo_promedio']:.6f} s, ")
                f.write(f"Aceleración: {row['aceleracion']:.2f}x, Eficiencia: {row['eficiencia']:.2f}\n")
            f.write("\n")
            
            # Impacto del OMP_THREAD_LIMIT
            f.write("IMPACTO DE OMP_THREAD_LIMIT\n")
            f.write("---------------------------\n")
            for limite in stats_limite['limite'].unique():
                f.write(f"Con límite = {limite}:\n")
                limite_data = stats_limite[stats_limite['limite'] == limite]
                for _, row in limite_data.iterrows():
                    f.write(f"  - {row['modo']}: {row['tiempo_promedio']:.6f} s\n")
            f.write("\n")
            
            # Conclusiones
            f.write("CONCLUSIONES\n")
            f.write("-----------\n")
            # Determinar qué modo es mejor en promedio
            modo_promedio = stats_hilos.groupby('modo')['tiempo_promedio'].mean().idxmin()
            # Determinar qué modo escala mejor
            mejor_escalabilidad = stats_hilos.groupby('modo')['aceleracion'].max().idxmax()
            
            f.write(f"1. El modo con mejor rendimiento promedio es: {modo_promedio}\n")
            f.write(f"2. El modo con mejor escalabilidad (mayor aceleración) es: {mejor_escalabilidad}\n")
            
            # Evaluar eficiencia paralela
            max_hilos = stats_hilos['num_hilos'].max()
            ef_max_hilos = stats_hilos[stats_hilos['num_hilos'] == max_hilos]['eficiencia'].max()
            f.write(f"3. La eficiencia con el máximo número de hilos ({max_hilos}) es: {ef_max_hilos:.2f}\n")
            
            # Encontrar punto de saturación aproximado
            for modo in stats_hilos['modo'].unique():
                modo_data = stats_hilos[stats_hilos['modo'] == modo].sort_values('num_hilos')
                tiempos = modo_data['tiempo_promedio'].values
                saturacion = False
                for i in range(1, len(tiempos)):
                    # Si el tiempo empeora en más de 5%, consideramos saturación
                    if tiempos[i] > tiempos[i-1] * 0.95:  
                        hilos_sat = modo_data.iloc[i-1]['num_hilos']
                        f.write(f"4. {modo} muestra signos de saturación a partir de {hilos_sat} hilos\n")
                        saturacion = True
                        break
                if not saturacion:
                    f.write(f"4. {modo} no muestra clara saturación en el rango de hilos analizado\n")
        
        print(f"Informes guardados en el directorio: {output_dir}")
        
    def analizar(self):
        """Ejecuta el análisis completo"""
        self.cargar_datos()
        stats_hilos, stats_limite = self.calcular_estadisticas()
        self.generar_visualizaciones(stats_hilos, stats_limite)
        self.generar_informes(stats_hilos, stats_limite)
        
        print("\nAnálisis completado exitosamente.")
        print("Resultados disponibles en el directorio 'resultados_analisis'.")


# Función principal para ejecutar el análisis
def main():
    print("=== ANÁLISIS DE RENDIMIENTO OPENMP ===")
    
    # Configurar el directorio donde se encuentran los datos
    data_dir = input("Introduce la ruta del directorio con los archivos de datos (presiona Enter para usar /tmp): ")
    data_dir = data_dir.strip() if data_dir.strip() else "/tmp"
    
    # Verificar que el directorio existe
    if not os.path.isdir(data_dir):
        print(f"Error: El directorio {data_dir} no existe.")
        return
    
    # Verificar que hay archivos relevantes
    archivos = glob.glob(os.path.join(data_dir, "tiempos*.txt")) + glob.glob(os.path.join(data_dir, "limite*.txt"))
    if not archivos:
        print(f"Error: No se encontraron archivos de datos en {data_dir}")
        return
    
    print(f"Se encontraron {len(archivos)} archivos de datos en {data_dir}")
    
    # Crear y ejecutar el analizador
    analizador = OpenMPAnalyzer(data_dir)
    analizador.analizar()


if __name__ == "__main__":
    main()

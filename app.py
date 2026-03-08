import os
from flask import Flask, render_template, request, jsonify
import jumper

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '').strip()
    manual_trend = data.get('trend', '').strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Perform analysis using jumper.py logic
        analysis_results = jumper.escandir_texto(text)
        
        # Calculate frequencies for automatic trend detection
        columna_silabas_v = [v[2] for v in analysis_results if len(v) > 2]
        versos_frecuentes_dict = jumper.most_frequent(columna_silabas_v)
        
        # Determine tendencia_versal
        if manual_trend and "Auto:" not in manual_trend:
            try:
                tendencia_versal = [int(i.strip()) for i in manual_trend.split(',') if i.strip().isdigit()]
            except:
                tendencia_versal = list(versos_frecuentes_dict.keys())
        else:
            tendencia_versal = list(versos_frecuentes_dict.keys())
            if not tendencia_versal and columna_silabas_v:
                tendencia_versal = sorted(list(set(columna_silabas_v)))

        # Prepare final data for frontend
        results = []
        precision_count = 0
        calidad_count = 0
        
        for i, v in enumerate(analysis_results):
            # v format: [original_verse, analyzed_verse, syllables, accents_list, ideal_accents, type_name, ratio]
            verse_text = v[0]
            analyzed_verse = v[1]
            syllables = v[2]
            accents = v[3]
            ideal_accents = v[4]
            type_name = v[5]
            ratio = int(v[6] * 100) if isinstance(v[6], (int, float)) else 0
            
            color = 'text-gray-900' # default
            if tendencia_versal:
                if syllables in tendencia_versal and ratio == 100:
                    precision_count += 1
                    color = 'text-green-600 font-medium'
                elif syllables in tendencia_versal:
                    precision_count += 1
                    color = 'text-gray-900'
                else:
                    color = 'text-red-600'
            
            if ratio == 100:
                calidad_count += 1
                
            results.append({
                'n': i + 1,
                'verse': verse_text,
                'analyzed': analyzed_verse,
                'syllables': syllables,
                'accents': str(accents),
                'ideal': str(ideal_accents),
                'type': type_name,
                'ratio': ratio,
                'color_class': color
            })

        total_verses = len(analysis_results)
        calidad_perc = (calidad_count / total_verses * 100) if total_verses > 0 else 0
        regularidad_perc = (precision_count / total_verses * 100) if total_verses > 0 else 0

        return jsonify({
            'results': results,
            'tendencia': tendencia_versal,
            'calidad': round(calidad_perc, 1),
            'regularidad': round(regularidad_perc, 1)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

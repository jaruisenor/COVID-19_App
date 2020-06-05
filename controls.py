# In[]:
# Controls for webapp
REGIONES ={
    '15': 'Arica y Parinacota', 
    '01': 'Tarapacá', 
    '02': 'Antofagasta', 
    '03': 'Atacama', 
    '04': 'Coquimbo', 
    '05': 'Valparaíso', 
    '13': 'Metropolitana', 
    '06': 'O’Higgins', 
    '07': 'Maule', 
    '16': 'Ñuble', 
    '08': 'Biobío', 
    '09': 'Araucanía', 
    '14': 'Los Ríos', 
    '10': 'Los Lagos', 
    '11': 'Aysén', 
    '12': 'Magallanes'}

ENFERMEDADES = dict(
    HP='Hipertensión arterial',
    DB='Diabetes',
    OB='Obesidad',
    EC='Enfermedad cardiovascular',
    CC='Cardiopatía crónica',
    EPC='Enfermedad pulmonar crónica',
    ERC='Enfermedad renal crónica',
    AS='Asma',
    ENC= 'Enfermedad neurológica crónica',
    INMU='Inmunocomprometido',
    EHC='Enfermedad hepática crónica')
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zero-Touch Rechnungs-Scanner</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f7f9fa;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            width: 100%;
            max-width: 480px;
            background: #ffffff;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            box-sizing: border-box;
        }
        h2 {
            font-size: 20px;
            margin-bottom: 8px;
            color: #111;
        }
        .privacy-badge {
            font-size: 12px;
            color: #0d6efd;
            background: #e7f1ff;
            padding: 6px 10px;
            border-radius: 6px;
            margin-bottom: 20px;
            display: inline-block;
        }
        .form-group {
            margin-bottom: 16px;
        }
        label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 6px;
        }
        input[type="email"], input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ced4da;
            border-radius: 8px;
            font-size: 16px; /* Предотвращает зум на iOS */
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 14px;
            background-color: #0d6efd;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
        }
        button:active {
            background-color: #0b5ed7;
        }
        #result {
            margin-top: 20px;
            background: #f1f3f5;
            padding: 14px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 13px;
            white-space: pre-wrap;
            display: none;
        }
        .loading {
            text-align: center;
            color: #6c757d;
            margin-top: 10px;
            display: none;
        }
    </style>
</head>
<body>

<div class="container">
    <h2>Rechnung hochladen</h2>
    <div class="privacy-badge">🔒 DSGVO-konform: Zero-Storage (Keine dauerhafte Speicherung)</div>

    <form id="uploadForm">
        <div class="form-group">
            <label for="email">Ihre E-Mail (Registrierungs-E-Mail):</label>
            <input type="email" id="email" required placeholder="name@firma.de">
        </div>

        <div class="form-group">
            <label for="file">Rechnung (PDF oder Bild):</label>
            <!-- Телефон автоматически предложит выбрать файл из памяти или галереи -->
            <input type="file" id="file" accept=".pdf,image/jpeg,image/png" required>
        </div>

        <button type="submit" id="submitBtn">Rechnung verarbeiten</button>
    </form>

    <div class="loading" id="loadingText">Verarbeitung läuft über KI... Bitte warten.</div>
    <div id="result"></div>
</div>

<script>
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingText = document.getElementById('loadingText');
    const resultDiv = document.getElementById('result');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const fileInput = document.getElementById('file');
        
        if (fileInput.files.length === 0) {
            alert('Bitte wählen Sie eine Datei aus.');
            return;
        }

        const formData = new FormData();
        formData.append('client_invoice_email', email);
        formData.append('file', fileInput.files[0]);

        submitBtn.style.display = 'none';
        loadingText.style.display = 'block';
        resultDiv.style.display = 'none';

        try {
            // Здесь будет адрес вашего развернутого бэкенда (например, на Render)
            const response = await fetch('https://your-backend-url.onrender.com/api/process-invoice', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                resultDiv.style.display = 'block';
                resultDiv.textContent = "Erfolgreich!\n\n" + JSON.stringify(data.extracted_data, null, 2);
            } else {
                alert('Fehler: ' + (data.detail || 'Unbekannter Fehler'));
            }
        } catch (error) {
            alert('Netzwerkfehler: ' + error.message);
        } finally {
            submitBtn.style.display = 'block';
            loadingText.style.display = 'none';
        }
    });
</script>

</body>
</html>

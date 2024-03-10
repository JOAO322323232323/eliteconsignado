const axios = require('axios')
const fs = require('fs');

const filePath = 'joao.csv'; 

if (!fs.existsSync(filePath)) {
    console.error('O arquivo não existe. Verifique o caminho do arquivo.');
    process.exit(1);
  }
  
  const fileContent = fs.readFileSync(filePath);
  
  const base64Data = fileContent.toString('base64');

axios.post(`http://localhost:8080/api/criar-campanha`, {
    base64Data: base64Data
})
.then(r => {
    console.log(r.data)
})
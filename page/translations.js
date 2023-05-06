// this script is responsible for translations
let lang = 'EN';
const langParam = new URLSearchParams(window.location.search).get('lang');
if(langParam?.toUpperCase() == 'LV')
  lang = 'LV';
else if(langParam?.toUpperCase() == 'EN')
  lang = 'EN'

let translationsJson = null;
const translatePage = () => {
  fetch('./translations.json')
  .then(response => response.json())
  .then(data => {
    translationsJson = data;
    let elemsTrans = document.querySelectorAll('.translate');
    elemsTrans.forEach((el) => {
      try{
        el.innerText = data[el.innerText][lang];
      }
      catch(err){
        throw new Error(`Cannot translate '${el.innerText}'`);
      }
    });
    let elemsTransPlaceholder = document.querySelectorAll('.translate-placeholder');
    elemsTransPlaceholder.forEach((el) => {
      try{
        el.placeholder = data[el.placeholder][lang];
      }
      catch(err){
        throw new Error(`Cannot translate '${el.placeholder}'`);
      }
    });
  })
  .catch(error => console.error(error))
};
translatePage();
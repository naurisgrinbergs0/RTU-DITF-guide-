// getting all required elements
const startCabinetSearchDropper = document.querySelector("#start_cabinet_search_dropper");
const endCabinetSearchDropper = document.querySelector("#end_cabinet_search_dropper");
const startCabinetInput = startCabinetSearchDropper.querySelector("#start_cabinet");
const endCabinetInput = endCabinetSearchDropper.querySelector("#end_cabinet");
const startCabinetSuggBox = startCabinetSearchDropper.querySelector("#start_cabinet_sugg_box");
const endCabinetSuggBox = endCabinetSearchDropper.querySelector("#end_cabinet_sugg_box");
const searchButton = document.querySelector("#btn-search");


// if user press any key and release
startCabinetInput.onkeyup = (e) => {
    onKeyUpEvent(startCabinetInput, startCabinetSuggBox, startCabinetSearchDropper, e);
}
endCabinetInput.onkeyup = (e) => {
    onKeyUpEvent(endCabinetInput, endCabinetSuggBox, endCabinetSearchDropper, e);
}
startCabinetInput.oninput = (e) =>{
    updateSearchButton();
}
endCabinetInput.oninput = (e) =>{
    updateSearchButton();
}

function onKeyUpEvent(inputElem, suggBox, searchDropper, e){
    let userData = e.target.value;
    let suggestions = [];
    
    suggestions = allCabinets.filter((data)=>{
        return data.cabinet.toLocaleLowerCase().startsWith(userData.toLocaleLowerCase());
    });
    suggestions = suggestions.map((data)=>{
        return data = `<li value="${data.id}">${data.cabinet}<span class="badge badge-dark">${translationsJson['floor'][lang]} ${data.floor}</span></li>`;
    });
    suggBox.style.display = 'block';
    showSuggestions(inputElem, suggBox, suggestions);
    let allList = suggBox.querySelectorAll("li");
    for (let i = 0; i < allList.length; i++)
        allList[i].setAttribute("onclick", `select('${inputElem.id}', '${suggBox.id}', '${searchDropper.id}', this)`);

    if (!userData)
        suggBox.style.display = 'none';
}

function select(inputElemId, suggBoxId, searchDropperId, element){
    const searchDropper = document.querySelector("#" + searchDropperId);
    const suggBox = searchDropper.querySelector("#" + suggBoxId);
    const inputElem = searchDropper.querySelector("#" + inputElemId);
    const selectData = allCabinets.find(el => el.id == element.value).cabinet;
    inputElem.value = selectData;
    inputElem.data = element.value;
    suggBox.style.display = 'none';
    updateSearchButton();
}

function showSuggestions(inputElem, suggBox, list){
    let listData;
    if(list.length > 1){
      listData = list.join('');
      suggBox.innerHTML = listData;
    }else{
        suggBox.style.display = 'none';
    }
}

function updateSearchButton(){
    // enable search button if both input values are valid
    const startCab = allCabinets.find(cab => cab.cabinet == startCabinetInput.value);
    const endCab = allCabinets.find(cab => cab.cabinet == endCabinetInput.value);
    if(startCab){
        searchButton.disabled = false;
        startCabinetInput.data = startCab.id;
        startCabinetSuggBox.style.display = 'none';
    }
    if(endCab){
        searchButton.disabled = false;
        endCabinetInput.data = endCab.id;
        endCabinetSuggBox.style.display = 'none';
    }
    if(!startCab || !endCab){
        searchButton.disabled = true;
    }
}
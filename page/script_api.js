    const allCabinets = [];
      fetch('/api/getcabinets')
      .then(response => response.json())
      .then(data => {
          data['cabinets'].forEach(cab => {
              allCabinets.push({ 
                id: cab.id, 
                cabinet: cab.cabinet,
                floor: cab.floor
              });
          });
      })
      .catch(error => {
          console.error('Error:', error);
      });

      const getDirections = () => {
        const start_cabinet = allCabinets.find(el => el.id == document.getElementById('start_cabinet').data)
        const end_cabinet = allCabinets.find(el => el.id == document.getElementById('end_cabinet').data)
        const useElevatorCheckbox = document.querySelector("#use_elevator_checkbox");

        const params = {
            cabinet_start: start_cabinet.cabinet,
            cabinet_end: end_cabinet.cabinet,
            floor_start: start_cabinet.floor,
            floor_end: end_cabinet.floor,
            use_elevator: useElevatorCheckbox.checked ? 1 : 0,
            language: lang
        };

        const queryString = new URLSearchParams(params).toString();

        fetch(`/api/getdirections?${queryString}`)
        .then(response => response.json())
        .then(data => {
            const dataJson = JSON.parse(data);

            const start_floor_text = document.getElementById("start_floor_text");
            const end_floor_text = document.getElementById("end_floor_text");
            const start_floor_img = document.getElementById("start_floor_img");
            const end_floor_img = document.getElementById("end_floor_img");
            const instructions_list = document.getElementById("instructions");

            start_floor_img.src = '../path_finder/path_pics/' + dataJson.start_floor_plan;
            start_floor_text.innerText = translationsJson['floor'][lang] + ' ' + dataJson.start_floor;
            if(dataJson.start_floor == dataJson.end_floor){
              end_floor_img.style.display = 'none';
              end_floor_text.style.display = 'none';
            }else{
              end_floor_img.style.display = 'inline';
              end_floor_img.src = '../path_finder/path_pics/' + dataJson.end_floor_plan;
              end_floor_text.style.display = 'inline';
              end_floor_text.innerText = translationsJson['floor'][lang] + ' ' + dataJson.end_floor;
            }
            Object.keys(dataJson.instructions).forEach((key) => {
                const li = document.createElement('li');
                li.innerText = dataJson.instructions[key];
                instructions_list.append(li);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
      };
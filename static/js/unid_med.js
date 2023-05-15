$(function(){

  function unid_med_change(){
    var id_materia_prima = $("#materia_prima").val();
    var url_format = "/unid_med/" + id_materia_prima + "/" + 1

    $.ajax({
      type: "GET",
      url: url_format
    }).done(function(data){
      $("#unidade_medida").attr("value", data.unidade_medida[1])
      $("#unidade_medida").prop("readonly", true);
    });
  }

  $("#materia_prima").change(function(){
    unid_med_change();
  });

  unid_med_change();
});
